package com.memorydebugger.app

import android.content.Context
import android.content.pm.PackageManager
import android.os.IBinder
import android.os.ParcelFileDescriptor
import android.util.Log
import dev.rikka.shizuku.Shizuku
import dev.rikka.shizuku.ShizukuBinderWrapper
import dev.rikka.shizuku.SystemServiceHelper
import java.io.File
import java.io.FileDescriptor
import java.io.FileInputStream
import java.io.FileOutputStream
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

/**
 * Memory access using Shizuku API
 * This provides elevated permissions without requiring full root access
 */
class ShizukuMemoryAccess(private val context: Context) {

    companion object {
        private const val TAG = "ShizukuMemoryAccess"
        private const val TIMEOUT_SECONDS = 5L
    }

    // Keep track of whether we have Shizuku permission
    private var hasShizukuPermission = false
    private var permissionRequestCode = 1000

    // Listener for permission changes
    private val permissionResultListener = object : Shizuku.OnRequestPermissionResultListener {
        override fun onRequestPermissionResult(requestCode: Int, grantResult: Int) {
            if (requestCode == permissionRequestCode) {
                hasShizukuPermission = grantResult == PackageManager.PERMISSION_GRANTED
                Log.d(TAG, "Shizuku permission result: $hasShizukuPermission")
            }
        }
    }

    init {
        // Register permission listener
        Shizuku.addRequestPermissionResultListener(permissionResultListener)
        
        // Check initial permission state
        checkShizukuPermission()
    }

    /**
     * Check if Shizuku is available and we have permission
     */
    fun checkShizukuPermission(): Boolean {
        // First check if Shizuku is installed
        if (!Shizuku.pingBinder()) {
            Log.e(TAG, "Shizuku is not available")
            return false
        }

        // Check if we already have permission
        if (Shizuku.checkSelfPermission() == PackageManager.PERMISSION_GRANTED) {
            hasShizukuPermission = true
            return true
        }

        // If we should show rationale
        if (Shizuku.shouldShowRequestPermissionRationale()) {
            Log.d(TAG, "Should show permission rationale")
            // In a real app, you'd show a dialog explaining why permission is needed
        }

        // Request permission
        try {
            Shizuku.requestPermission(permissionRequestCode)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to request Shizuku permission", e)
            hasShizukuPermission = false
            return false
        }

        return false // We're in the process of requesting, so return false for now
    }

    /**
     * Get a list of running processes using Shizuku
     */
    fun listProcesses(): List<ProcessInfo> {
        if (!hasShizukuPermission && !checkShizukuPermission()) {
            Log.e(TAG, "No Shizuku permission to list processes")
            return emptyList()
        }

        return try {
            // Get the activity manager service
            val activityManager = SystemServiceHelper.getSystemService("activity")
            
            // This needs reflection since the internal interfaces aren't directly accessible
            val method = Class.forName("android.app.IActivityManager")
                .getDeclaredMethod("getRunningAppProcesses")
            
            @Suppress("UNCHECKED_CAST")
            val processes = method.invoke(activityManager) as? List<Any> ?: emptyList()
            
            processes.mapNotNull { process ->
                try {
                    // Extract process info using reflection
                    val processClass = process.javaClass
                    val pidField = processClass.getDeclaredField("pid")
                    val pkgListField = processClass.getDeclaredField("pkgList")
                    val processNameField = processClass.getDeclaredField("processName")
                    
                    val pid = pidField.get(process) as Int
                    val pkgList = pkgListField.get(process) as Array<*>
                    val processName = processNameField.get(process) as String
                    
                    ProcessInfo(
                        pid = pid.toString(),
                        name = processName,
                        packageNames = pkgList.map { it.toString() }
                    )
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to extract process info", e)
                    null
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to list processes using Shizuku", e)
            emptyList()
        }
    }

    /**
     * Read memory from a process using Shizuku
     */
    fun readMemory(pid: String, address: String, size: Int): ByteArray? {
        if (!hasShizukuPermission && !checkShizukuPermission()) {
            Log.e(TAG, "No Shizuku permission to read memory")
            return null
        }

        try {
            // Convert address to a long
            val addressLong = address.toLongOrNull(16)
                ?: throw IllegalArgumentException("Invalid address format: $address")

            // We'll use a shell command through Shizuku to read memory
            val latch = CountDownLatch(1)
            val result = AtomicReference<ByteArray?>(null)

            // Get a shell interface
            val shell = Shizuku.newProcess(arrayOf("sh"), null, null)
            
            // Create a temp file to hold the memory data
            val tempFile = File.createTempFile("memory", ".bin", context.cacheDir)
            tempFile.deleteOnExit()

            // Command to read memory and write to temp file
            val command = "dd if=/proc/$pid/mem bs=1 count=$size skip=$addressLong of=${tempFile.absolutePath} 2>/dev/null\n"
            
            // Execute the command
            val outputStream = shell.outputStream
            outputStream.write(command.toByteArray())
            outputStream.flush()
            
            // Wait for command to complete
            Thread.sleep(200)  // Short delay to ensure command completion
            
            // Read the temp file
            val memory = tempFile.readBytes()
            
            // Clean up
            tempFile.delete()
            shell.destroy()
            
            return if (memory.isEmpty()) null else memory
        } catch (e: Exception) {
            Log.e(TAG, "Failed to read memory using Shizuku", e)
            return null
        }
    }

    /**
     * Write memory to a process using Shizuku
     */
    fun writeMemory(pid: String, address: String, data: ByteArray): Boolean {
        if (!hasShizukuPermission && !checkShizukuPermission()) {
            Log.e(TAG, "No Shizuku permission to write memory")
            return false
        }

        try {
            // Convert address to a long
            val addressLong = address.toLongOrNull(16)
                ?: throw IllegalArgumentException("Invalid address format: $address")

            // Create a temp file with the data
            val tempFile = File.createTempFile("memory_write", ".bin", context.cacheDir)
            tempFile.deleteOnExit()
            tempFile.writeBytes(data)

            // Get a shell interface
            val shell = Shizuku.newProcess(arrayOf("sh"), null, null)
            
            // Command to write from temp file to memory
            val command = "dd if=${tempFile.absolutePath} of=/proc/$pid/mem bs=${data.size} count=1 seek=$addressLong conv=notrunc 2>/dev/null\n"
            
            // Execute the command
            val outputStream = shell.outputStream
            outputStream.write(command.toByteArray())
            outputStream.flush()
            
            // Wait for command to complete
            Thread.sleep(200)  // Short delay to ensure command completion
            
            // Clean up
            tempFile.delete()
            shell.destroy()
            
            return true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to write memory using Shizuku", e)
            return false
        }
    }

    /**
     * Get memory regions for a process
     */
    fun getMemoryRegions(pid: String): List<MemoryRegion> {
        if (!hasShizukuPermission && !checkShizukuPermission()) {
            Log.e(TAG, "No Shizuku permission to get memory regions")
            return emptyList()
        }

        try {
            // We'll use a shell command through Shizuku to read memory maps
            val shell = Shizuku.newProcess(arrayOf("sh"), null, null)
            
            // Command to read memory maps
            val command = "cat /proc/$pid/maps\n"
            
            // Execute the command
            val outputStream = shell.outputStream
            outputStream.write(command.toByteArray())
            outputStream.flush()
            
            // Read the output
            val inputStream = shell.inputStream
            val buffer = ByteArray(8192)
            var bytesRead = inputStream.read(buffer)
            val output = StringBuilder()
            
            while (bytesRead > 0) {
                output.append(String(buffer, 0, bytesRead))
                bytesRead = inputStream.read(buffer)
            }
            
            // Clean up
            shell.destroy()
            
            // Parse the maps file
            return parseMapsOutput(output.toString())
        } catch (e: Exception) {
            Log.e(TAG, "Failed to get memory regions using Shizuku", e)
            return emptyList()
        }
    }

    /**
     * Parse the output of /proc/[pid]/maps
     */
    private fun parseMapsOutput(output: String): List<MemoryRegion> {
        val regions = mutableListOf<MemoryRegion>()
        
        // Split the output by lines
        val lines = output.split("\n")
        
        for (line in lines) {
            if (line.isBlank()) continue
            
            try {
                // Each line is in the format: 
                // address perms offset dev inode pathname
                val parts = line.trim().split("\\s+".toRegex(), 6)
                
                if (parts.size < 5) continue
                
                // Parse address range (e.g., "00400000-00452000")
                val addrRange = parts[0].split("-")
                if (addrRange.size != 2) continue
                
                val startAddr = addrRange[0].toLongOrNull(16) ?: continue
                val endAddr = addrRange[1].toLongOrNull(16) ?: continue
                val size = endAddr - startAddr
                
                // Parse permissions (e.g., "r-xp")
                val perms = parts[1]
                
                // Path is optional (anonymous mappings don't have it)
                val path = if (parts.size > 5) parts[5] else ""
                
                regions.add(
                    MemoryRegion(
                        baseAddress = "0x${addrRange[0]}",
                        endAddress = "0x${addrRange[1]}",
                        size = size,
                        permissions = perms,
                        path = path,
                        type = if (path.isNotEmpty()) "file" else "anonymous"
                    )
                )
            } catch (e: Exception) {
                Log.e(TAG, "Failed to parse memory region: $line", e)
                continue
            }
        }
        
        return regions
    }

    /**
     * Check if Shizuku is available
     */
    fun isShizukuAvailable(): Boolean {
        return Shizuku.pingBinder()
    }

    /**
     * Cleanup resources
     */
    fun cleanup() {
        Shizuku.removeRequestPermissionResultListener(permissionResultListener)
    }

    /**
     * Data class for process information
     */
    data class ProcessInfo(
        val pid: String,
        val name: String,
        val packageNames: List<String> = emptyList()
    )

    /**
     * Data class for memory region information
     */
    data class MemoryRegion(
        val baseAddress: String,
        val endAddress: String,
        val size: Long,
        val permissions: String,
        val path: String,
        val type: String
    )
}