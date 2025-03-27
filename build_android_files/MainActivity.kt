package com.memorydebugger.app

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.RadioButton
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import dev.rikka.shizuku.Shizuku
import eu.chainfire.libsuperuser.Shell
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.button.MaterialButton
import com.google.android.material.card.MaterialCardView
import com.google.android.material.textfield.TextInputEditText

class MainActivity : AppCompatActivity() {

    private lateinit var tvAccessStatus: TextView
    private lateinit var processList: RecyclerView
    private lateinit var btnRefreshProcesses: MaterialButton
    private lateinit var processAdapter: ProcessAdapter
    private lateinit var cardMemoryOperations: MaterialCardView
    private lateinit var tvSelectedProcess: TextView
    private lateinit var etMemoryAddress: TextInputEditText
    private lateinit var etMemorySize: TextInputEditText
    private lateinit var etMemoryValue: TextInputEditText
    private lateinit var btnReadMemory: MaterialButton
    private lateinit var btnWriteMemory: MaterialButton
    private lateinit var btnViewMemoryRegions: MaterialButton
    private lateinit var btnLaunchWebview: MaterialButton
    private lateinit var btnCheckPermission: MaterialButton
    private lateinit var rbShizuku: RadioButton
    private lateinit var rbRoot: RadioButton

    private var shizukuAccess: ShizukuMemoryAccess? = null
    private var nativeAccess: NativeMemoryAccess? = null
    private var selectedProcess: ProcessInfo? = null
    private var useShizuku = true // Default to Shizuku

    private val shizukuBinderReceiver = object : Shizuku.OnBinderReceivedListener {
        override fun onBinderReceived() {
            updateAccessStatus()
        }
    }

    private val shizukuBinderDeadListener = object : Shizuku.OnBinderDeadListener {
        override fun onBinderDead() {
            updateAccessStatus()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        initViews()
        setupShizuku()
        setupNative()
        setupListeners()
        updateAccessStatus()
    }

    private fun initViews() {
        tvAccessStatus = findViewById(R.id.tvAccessStatus)
        processList = findViewById(R.id.processList)
        btnRefreshProcesses = findViewById(R.id.btnRefreshProcesses)
        cardMemoryOperations = findViewById(R.id.cardMemoryOperations)
        tvSelectedProcess = findViewById(R.id.tvSelectedProcess)
        etMemoryAddress = findViewById(R.id.etMemoryAddress)
        etMemorySize = findViewById(R.id.etMemorySize)
        etMemoryValue = findViewById(R.id.etMemoryValue)
        btnReadMemory = findViewById(R.id.btnReadMemory)
        btnWriteMemory = findViewById(R.id.btnWriteMemory)
        btnViewMemoryRegions = findViewById(R.id.btnViewMemoryRegions)
        btnLaunchWebview = findViewById(R.id.btnLaunchWebview)
        btnCheckPermission = findViewById(R.id.btnCheckPermission)
        rbShizuku = findViewById(R.id.rbShizuku)
        rbRoot = findViewById(R.id.rbRoot)

        // Setup RecyclerView
        processAdapter = ProcessAdapter(emptyList()) { process ->
            onProcessSelected(process)
        }
        processList.apply {
            layoutManager = LinearLayoutManager(this@MainActivity)
            adapter = processAdapter
        }
    }

    private fun setupShizuku() {
        shizukuAccess = ShizukuMemoryAccess(this)
        Shizuku.addBinderReceivedListener(shizukuBinderReceiver)
        Shizuku.addBinderDeadListener(shizukuBinderDeadListener)
    }

    private fun setupNative() {
        try {
            nativeAccess = NativeMemoryAccess()
        } catch (e: Exception) {
            // Native library failed to load, this is handled gracefully
        }
    }

    private fun setupListeners() {
        btnRefreshProcesses.setOnClickListener {
            refreshProcessList()
        }

        btnReadMemory.setOnClickListener {
            readMemory()
        }

        btnWriteMemory.setOnClickListener {
            writeMemory()
        }

        btnViewMemoryRegions.setOnClickListener {
            viewMemoryRegions()
        }

        btnLaunchWebview.setOnClickListener {
            launchWebView()
        }

        btnCheckPermission.setOnClickListener {
            checkPermissions()
        }

        rbShizuku.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                useShizuku = true
                updateAccessStatus()
            }
        }

        rbRoot.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                useShizuku = false
                updateAccessStatus()
            }
        }
    }

    private fun updateAccessStatus() {
        lifecycleScope.launch {
            val statusText = withContext(Dispatchers.IO) {
                if (useShizuku) {
                    if (shizukuAccess?.isShizukuAvailable() == true) {
                        if (shizukuAccess?.checkShizukuPermission() == true) {
                            "Status: Shizuku is available and permitted"
                        } else {
                            "Status: Shizuku is available but not permitted"
                        }
                    } else {
                        "Status: Shizuku is not available"
                    }
                } else {
                    if (nativeAccess?.isRooted() == true) {
                        "Status: Root access is available"
                    } else {
                        "Status: Root access is not available"
                    }
                }
            }

            tvAccessStatus.text = statusText
        }
    }

    private fun checkPermissions() {
        if (useShizuku) {
            if (shizukuAccess?.checkShizukuPermission() == true) {
                Toast.makeText(this, "Shizuku permission already granted", Toast.LENGTH_SHORT).show()
            } else {
                // Permission request will be handled by the ShizukuMemoryAccess class
                shizukuAccess?.checkShizukuPermission()
                Toast.makeText(this, "Requesting Shizuku permission...", Toast.LENGTH_SHORT).show()
            }
        } else {
            if (nativeAccess?.isRooted() == true) {
                Toast.makeText(this, "Root access is available", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this, "Root access is not available. This device may not be rooted.", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun refreshProcessList() {
        lifecycleScope.launch {
            val processes = withContext(Dispatchers.IO) {
                if (useShizuku) {
                    shizukuAccess?.listProcesses() ?: emptyList()
                } else {
                    try {
                        val jsonStr = nativeAccess?.listProcessesRoot() ?: "[]"
                        parseProcessJson(jsonStr)
                    } catch (e: Exception) {
                        emptyList<ProcessInfo>()
                    }
                }
            }

            // Update adapter
            processAdapter.updateProcesses(processes)
            
            if (processes.isEmpty()) {
                Toast.makeText(this@MainActivity, "No processes found or permission denied", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun parseProcessJson(jsonStr: String): List<ProcessInfo> {
        // Basic JSON parsing - in a real app, use a proper JSON library
        return try {
            if (jsonStr == "[]") return emptyList()
            
            val result = mutableListOf<ProcessInfo>()
            // Very basic JSON parsing
            val items = jsonStr.trim('[', ']').split("},{")
            
            for (item in items) {
                val pidMatch = Regex("\"pid\":\"(\\d+)\"").find(item)
                val nameMatch = Regex("\"name\":\"([^\"]+)\"").find(item)
                
                if (pidMatch != null && nameMatch != null) {
                    val pid = pidMatch.groupValues[1]
                    val name = nameMatch.groupValues[1]
                    result.add(ProcessInfo(pid, name, emptyList()))
                }
            }
            
            result
        } catch (e: Exception) {
            emptyList()
        }
    }

    private fun onProcessSelected(process: ProcessInfo) {
        selectedProcess = process
        tvSelectedProcess.text = "Selected process: ${process.name} (PID: ${process.pid})"
        cardMemoryOperations.visibility = View.VISIBLE
    }

    private fun readMemory() {
        val pid = selectedProcess?.pid ?: return
        val address = etMemoryAddress.text.toString()
        val sizeStr = etMemorySize.text.toString()
        
        if (address.isBlank() || sizeStr.isBlank()) {
            Toast.makeText(this, "Please enter address and size", Toast.LENGTH_SHORT).show()
            return
        }
        
        val size = sizeStr.toIntOrNull() ?: 8
        
        lifecycleScope.launch {
            try {
                val result = withContext(Dispatchers.IO) {
                    if (useShizuku) {
                        shizukuAccess?.readMemory(pid, address, size)
                    } else {
                        val hexStr = nativeAccess?.readMemoryRoot(pid, address, size) ?: return@withContext null
                        hexStr.chunked(2).map { it.toInt(16).toByte() }.toByteArray()
                    }
                }
                
                if (result != null) {
                    val hexString = result.joinToString("") { 
                        String.format("%02X", it.toInt() and 0xFF) 
                    }
                    etMemoryValue.setText(hexString)
                } else {
                    Toast.makeText(this@MainActivity, "Failed to read memory", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "Error: ${e.localizedMessage}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun writeMemory() {
        val pid = selectedProcess?.pid ?: return
        val address = etMemoryAddress.text.toString()
        val value = etMemoryValue.text.toString()
        
        if (address.isBlank() || value.isBlank()) {
            Toast.makeText(this, "Please enter address and value", Toast.LENGTH_SHORT).show()
            return
        }
        
        lifecycleScope.launch {
            try {
                val result = withContext(Dispatchers.IO) {
                    if (useShizuku) {
                        val byteData = value.chunked(2).map { 
                            it.toInt(16).toByte() 
                        }.toByteArray()
                        shizukuAccess?.writeMemory(pid, address, byteData) ?: false
                    } else {
                        nativeAccess?.writeMemoryRoot(pid, address, value) ?: false
                    }
                }
                
                if (result) {
                    Toast.makeText(this@MainActivity, "Memory written successfully", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this@MainActivity, "Failed to write memory", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "Error: ${e.localizedMessage}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun viewMemoryRegions() {
        val pid = selectedProcess?.pid ?: return
        
        lifecycleScope.launch {
            try {
                val regions = withContext(Dispatchers.IO) {
                    if (useShizuku) {
                        shizukuAccess?.getMemoryRegions(pid) ?: emptyList()
                    } else {
                        // Not implemented for simplicity in this sample
                        emptyList<ShizukuMemoryAccess.MemoryRegion>()
                    }
                }
                
                if (regions.isNotEmpty()) {
                    showMemoryRegionsDialog(regions)
                } else {
                    Toast.makeText(this@MainActivity, "No memory regions found or not supported", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "Error: ${e.localizedMessage}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun showMemoryRegionsDialog(regions: List<ShizukuMemoryAccess.MemoryRegion>) {
        val regionTexts = regions.take(100).map { region ->
            "${region.baseAddress}-${region.endAddress} [${region.permissions}] ${region.path}"
        }
        
        MaterialAlertDialogBuilder(this)
            .setTitle("Memory Regions")
            .setItems(regionTexts.toTypedArray(), null)
            .setPositiveButton("Close", null)
            .setNeutralButton("Copy First Region to Address") { _, _ ->
                if (regions.isNotEmpty()) {
                    etMemoryAddress.setText(regions[0].baseAddress.removePrefix("0x"))
                }
            }
            .show()
    }

    private fun launchWebView() {
        val intent = Intent(this, WebViewActivity::class.java)
        startActivity(intent)
    }

    override fun onDestroy() {
        super.onDestroy()
        Shizuku.removeBinderReceivedListener(shizukuBinderReceiver)
        Shizuku.removeBinderDeadListener(shizukuBinderDeadListener)
        shizukuAccess?.cleanup()
    }

    data class ProcessInfo(
        val pid: String,
        val name: String,
        val packageNames: List<String> = emptyList()
    )
}