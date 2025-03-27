package com.memorydebugger.app

import android.content.Context
import android.webkit.JavascriptInterface
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

/**
 * JavaScript interface to communicate between WebView and Android
 */
class WebAppInterface(
    private val context: Context,
    private val activity: AppCompatActivity
) {
    /**
     * Show a toast message from JavaScript
     */
    @JavascriptInterface
    fun showToast(message: String) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }

    /**
     * Check if Shizuku is available
     */
    @JavascriptInterface
    fun isShizukuAvailable(): Boolean {
        val shizukuAccess = ShizukuMemoryAccess(context)
        return shizukuAccess.isShizukuAvailable()
    }

    /**
     * Check if device is rooted
     */
    @JavascriptInterface
    fun isRooted(): Boolean {
        val nativeAccess = NativeMemoryAccess()
        return nativeAccess.isRooted()
    }

    /**
     * List processes using Shizuku
     */
    @JavascriptInterface
    fun listProcessesShizuku(): String {
        val shizukuAccess = ShizukuMemoryAccess(context)
        val processes = shizukuAccess.listProcesses()
        
        // Convert to JSON
        val jsonBuilder = StringBuilder("[")
        processes.forEachIndexed { index, process ->
            if (index > 0) jsonBuilder.append(",")
            jsonBuilder.append("{\"pid\":\"${process.pid}\",\"name\":\"${process.name.replace("\"", "\\\"")}\",\"packageNames\":[")
            process.packageNames.forEachIndexed { pkgIndex, pkg ->
                if (pkgIndex > 0) jsonBuilder.append(",")
                jsonBuilder.append("\"${pkg.replace("\"", "\\\"")}\"")
            }
            jsonBuilder.append("]}")
        }
        jsonBuilder.append("]")
        
        return jsonBuilder.toString()
    }

    /**
     * List processes using root
     */
    @JavascriptInterface
    fun listProcessesRoot(): String {
        val nativeAccess = NativeMemoryAccess()
        return nativeAccess.listProcessesRoot()
    }

    /**
     * Read memory using Shizuku
     */
    @JavascriptInterface
    fun readMemoryShizuku(pid: String, address: String, size: Int): String {
        val shizukuAccess = ShizukuMemoryAccess(context)
        val bytes = shizukuAccess.readMemory(pid, address, size) ?: return ""
        
        // Convert to hex string
        val hexBuilder = StringBuilder()
        for (byte in bytes) {
            hexBuilder.append(String.format("%02X", byte.toInt() and 0xFF))
        }
        
        return hexBuilder.toString()
    }

    /**
     * Read memory using root
     */
    @JavascriptInterface
    fun readMemoryRoot(pid: String, address: String, size: Int): String {
        val nativeAccess = NativeMemoryAccess()
        return nativeAccess.readMemoryRoot(pid, address, size)
    }

    /**
     * Write memory using Shizuku
     */
    @JavascriptInterface
    fun writeMemoryShizuku(pid: String, address: String, hexValue: String): Boolean {
        val shizukuAccess = ShizukuMemoryAccess(context)
        
        // Convert hex string to byte array
        val bytes = try {
            hexValue.chunked(2).map { it.toInt(16).toByte() }.toByteArray()
        } catch (e: Exception) {
            return false
        }
        
        return shizukuAccess.writeMemory(pid, address, bytes)
    }

    /**
     * Write memory using root
     */
    @JavascriptInterface
    fun writeMemoryRoot(pid: String, address: String, hexValue: String): Boolean {
        val nativeAccess = NativeMemoryAccess()
        return nativeAccess.writeMemoryRoot(pid, address, hexValue)
    }

    /**
     * Get memory regions using Shizuku
     */
    @JavascriptInterface
    fun getMemoryRegionsShizuku(pid: String): String {
        val shizukuAccess = ShizukuMemoryAccess(context)
        val regions = shizukuAccess.getMemoryRegions(pid)
        
        // Convert to JSON
        val jsonBuilder = StringBuilder("[")
        regions.forEachIndexed { index, region ->
            if (index > 0) jsonBuilder.append(",")
            jsonBuilder.append("{\"baseAddress\":\"${region.baseAddress}\",")
            jsonBuilder.append("\"endAddress\":\"${region.endAddress}\",")
            jsonBuilder.append("\"size\":${region.size},")
            jsonBuilder.append("\"permissions\":\"${region.permissions}\",")
            jsonBuilder.append("\"path\":\"${region.path.replace("\"", "\\\"")}\",")
            jsonBuilder.append("\"type\":\"${region.type}\"}")
        }
        jsonBuilder.append("]")
        
        return jsonBuilder.toString()
    }

    /**
     * Request Shizuku permission
     */
    @JavascriptInterface
    fun requestShizukuPermission(): Boolean {
        val shizukuAccess = ShizukuMemoryAccess(context)
        return shizukuAccess.checkShizukuPermission()
    }

    /**
     * Close the current activity
     */
    @JavascriptInterface
    fun closeWebView() {
        activity.finish()
    }
}