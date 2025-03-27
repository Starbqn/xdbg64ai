"""
Build script for Memory Debugger Android version.
This script prepares the web application to be embedded in an Android WebView.
"""
import os
import shutil
import subprocess
import sys
import json
from pathlib import Path

# Define paths
CURRENT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
ANDROID_DIR = CURRENT_DIR / "android"
ANDROID_ASSETS_DIR = ANDROID_DIR / "app" / "src" / "main" / "assets"
ANDROID_RES_DIR = ANDROID_DIR / "app" / "src" / "main" / "res"

def setup_android_project():
    """Set up the basic Android project structure using Android Studio."""
    print("Setting up Android project structure...")
    
    # Create Android project directory if it doesn't exist
    if not ANDROID_DIR.exists():
        ANDROID_DIR.mkdir(parents=True)
        
    # Check if Android Studio is installed and in PATH
    try:
        # This will create a new Android project
        # Note: This requires Android Studio CLI to be in PATH
        cmd = [
            "studio", "create", "project", 
            "--language", "kotlin",
            "--package-name", "com.memorydebugger.app",
            "--activity-name", "MainActivity",
            "--location", str(ANDROID_DIR)
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print("Android project created successfully.")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Failed to create Android project. Make sure Android Studio is installed.")
        print("Manual setup instructions:")
        print("1. Open Android Studio")
        print("2. Create a new project with:")
        print("   - Package name: com.memorydebugger.app")
        print("   - Activity name: MainActivity")
        print("   - Location: " + str(ANDROID_DIR))
        return False

def create_webview_integration():
    """Create the necessary files to integrate WebView."""
    print("Creating WebView integration files...")
    
    # Create MainActivity.kt
    main_activity_path = ANDROID_DIR / "app" / "src" / "main" / "java" / "com" / "memorydebugger" / "app" / "MainActivity.kt"
    main_activity_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(main_activity_path, 'w') as f:
        f.write("""
package com.memorydebugger.app

import android.annotation.SuppressLint
import android.os.Bundle
import android.webkit.WebSettings
import android.webkit.WebView
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    private lateinit var webView: WebView
    
    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        webView = findViewById(R.id.webView)
        
        // Enable JavaScript
        val webSettings: WebSettings = webView.settings
        webSettings.javaScriptEnabled = true
        webSettings.domStorageEnabled = true
        webSettings.allowFileAccess = true
        
        // Load the web app from assets
        webView.loadUrl("file:///android_asset/index.html")
        
        // Add bridge between JavaScript and Android
        webView.addJavascriptInterface(WebAppInterface(this), "Android")
    }
}
        """.strip())
    
    # Create WebAppInterface.kt for JavaScript bridge
    web_interface_path = ANDROID_DIR / "app" / "src" / "main" / "java" / "com" / "memorydebugger" / "app" / "WebAppInterface.kt"
    with open(web_interface_path, 'w') as f:
        f.write("""
package com.memorydebugger.app

import android.content.Context
import android.webkit.JavascriptInterface
import android.widget.Toast

class WebAppInterface(private val context: Context) {
    
    @JavascriptInterface
    fun showToast(message: String) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }
    
    // Add methods for memory reading/writing on Android
    // This will require native code and permissions
    // For a prototype, these can be stubs
    
    @JavascriptInterface
    fun listProcesses(): String {
        // This would need native implementation using JNI
        // For now, return mock data
        return "[]"
    }
    
    @JavascriptInterface
    fun readMemory(processId: String, address: String): String {
        // This would need native implementation using JNI
        return "null"
    }
    
    @JavascriptInterface
    fun writeMemory(processId: String, address: String, value: String): Boolean {
        // This would need native implementation using JNI
        return false
    }
}
        """.strip())
    
    # Create activity_main.xml layout
    layout_path = ANDROID_DIR / "app" / "src" / "main" / "res" / "layout"
    layout_path.mkdir(parents=True, exist_ok=True)
    
    with open(layout_path / "activity_main.xml", 'w') as f:
        f.write("""
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <WebView
        android:id="@+id/webView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
        """.strip())
    
    # Update AndroidManifest.xml to add internet permission
    manifest_path = ANDROID_DIR / "app" / "src" / "main" / "AndroidManifest.xml"
    
    # This is a basic manifest, would need to be adjusted based on actual generated manifest
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            manifest_content = f.read()
        
        # Add internet permission if not already present
        if "<uses-permission android:name=\"android.permission.INTERNET\" />" not in manifest_content:
            manifest_content = manifest_content.replace("<manifest", 
                "<manifest\n    xmlns:tools=\"http://schemas.android.com/tools\"")
            manifest_content = manifest_content.replace("</manifest>", 
                "    <uses-permission android:name=\"android.permission.INTERNET\" />\n</manifest>")
        
        with open(manifest_path, 'w') as f:
            f.write(manifest_content)
    
    print("WebView integration files created successfully.")

def prepare_web_assets():
    """Prepare web assets for inclusion in the Android app."""
    print("Preparing web assets...")
    
    # Create assets directory
    assets_dir = ANDROID_ASSETS_DIR
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # Create modified index.html for Android compatibility
    with open(assets_dir / "index.html", 'w') as f:
        f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Memory Debugger</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f0f0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .process-list {
            list-style: none;
            padding: 0;
        }
        .process-item {
            margin-bottom: 10px;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
            cursor: pointer;
        }
        .process-item:hover {
            background-color: #efefef;
        }
        .button {
            display: inline-block;
            padding: 8px 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 8px;
        }
        .button:hover {
            background-color: #45a049;
        }
        .note {
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 4px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Memory Debugger</h1>
        
        <p>Mobile Version</p>
        
        <div class="note">
            <p><strong>Note:</strong> The Android version has limited functionality compared to the desktop version. 
            Some features may require root access.</p>
        </div>
        
        <h2>System Processes</h2>
        <div id="process-list-container">
            <ul class="process-list" id="processList">
                <li>Loading processes...</li>
            </ul>
        </div>
        
        <button class="button" id="refreshButton">Refresh Processes</button>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Function to fetch and display processes
            function loadProcesses() {
                try {
                    // Call Android bridge to get processes
                    const processesJson = Android.listProcesses();
                    const processes = JSON.parse(processesJson);
                    
                    const processList = document.getElementById('processList');
                    processList.innerHTML = '';
                    
                    if (processes.length === 0) {
                        processList.innerHTML = '<li>No processes available or insufficient permissions</li>';
                        return;
                    }
                    
                    processes.forEach(process => {
                        const li = document.createElement('li');
                        li.className = 'process-item';
                        li.textContent = `${process.name} (PID: ${process.pid})`;
                        li.addEventListener('click', function() {
                            Android.showToast(`Selected process: ${process.name}`);
                            // In the future, this would open process details
                        });
                        processList.appendChild(li);
                    });
                    
                } catch (error) {
                    console.error('Error loading processes:', error);
                    document.getElementById('processList').innerHTML = 
                        '<li>Error loading processes. This may require root access.</li>';
                }
            }
            
            // Setup refresh button
            document.getElementById('refreshButton').addEventListener('click', loadProcesses);
            
            // Initial load
            loadProcesses();
        });
    </script>
</body>
</html>
        """.strip())
    
    print("Web assets prepared successfully.")

def create_gradle_files():
    """Create or update Gradle build files."""
    print("Creating Gradle build files...")
    
    # Create build.gradle (app)
    app_gradle_path = ANDROID_DIR / "app" / "build.gradle"
    
    app_gradle_content = """
plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    namespace 'com.memorydebugger.app'
    compileSdk 34

    defaultConfig {
        applicationId "com.memorydebugger.app"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"

        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = '1.8'
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.10.1'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'androidx.recyclerview:recyclerview:1.3.2'
    implementation 'androidx.cardview:cardview:1.0.0'
    implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.2'
    implementation 'androidx.lifecycle:lifecycle-livedata-ktx:2.6.2'
    implementation 'androidx.navigation:navigation-fragment-ktx:2.7.0'
    implementation 'androidx.navigation:navigation-ui-ktx:2.7.0'
    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
    
    // For memory access (root devices only)
    implementation 'eu.chainfire:libsuperuser:1.1.1'
    
    // Shizuku API for elevated permissions without full root
    implementation 'dev.rikka.shizuku:api:13.1.4'
    implementation 'dev.rikka.shizuku:provider:13.1.4'
}
"""
    
    with open(app_gradle_path, 'w') as f:
        f.write(app_gradle_content.strip())
    
    # Create settings.gradle
    settings_gradle_path = ANDROID_DIR / "settings.gradle"
    
    settings_gradle_content = """
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "MemoryDebugger"
include ':app'
"""
    
    with open(settings_gradle_path, 'w') as f:
        f.write(settings_gradle_content.strip())
    
    # Create build.gradle (project)
    project_gradle_path = ANDROID_DIR / "build.gradle"
    
    project_gradle_content = """
// Top-level build file where you can add configuration options common to all sub-projects/modules.
plugins {
    id 'com.android.application' version '8.0.2' apply false
    id 'com.android.library' version '8.0.2' apply false
    id 'org.jetbrains.kotlin.android' version '1.8.20' apply false
}
"""
    
    with open(project_gradle_path, 'w') as f:
        f.write(project_gradle_content.strip())
    
    # Create gradle.properties
    gradle_properties_path = ANDROID_DIR / "gradle.properties"
    
    gradle_properties_content = """
# Project-wide Gradle settings.
# IDE (e.g. Android Studio) users:
# Gradle settings configured through the IDE *will override*
# any settings specified in this file.
# For more details on how to configure your build environment visit
# http://www.gradle.org/docs/current/userguide/build_environment.html
# Specifies the JVM arguments used for the daemon process.
# The setting is particularly useful for tweaking memory settings.
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
# When configured, Gradle will run in incubating parallel mode.
# This option should only be used with decoupled projects. More details, visit
# http://www.gradle.org/docs/current/userguide/multi_project_builds.html#sec:decoupled_projects
# org.gradle.parallel=true
# AndroidX package structure to make it clearer which packages are bundled with the
# Android operating system, and which are packaged with your app's APK
# https://developer.android.com/topic/libraries/support-library/androidx-rn
android.useAndroidX=true
# Kotlin code style for this project: "official" or "obsolete":
kotlin.code.style=official
# Enables namespacing of each library's R class so that its R class includes only the
# resources declared in the library itself and none from the library's dependencies,
# thereby reducing the size of the R class for that library
android.nonTransitiveRClass=true
"""
    
    with open(gradle_properties_path, 'w') as f:
        f.write(gradle_properties_content.strip())
    
    print("Gradle build files created successfully.")

def create_native_code():
    """Create native code implementation for memory access."""
    print("Creating native code files...")
    
    # Create directory for native code
    cpp_dir = ANDROID_DIR / "app" / "src" / "main" / "cpp"
    cpp_dir.mkdir(parents=True, exist_ok=True)
    
    # Create CMakeLists.txt
    cmake_path = cpp_dir / "CMakeLists.txt"
    
    with open(cmake_path, 'w') as f:
        f.write("""
cmake_minimum_required(VERSION 3.18.1)
project(memorydebugger)

add_library(memorydebugger SHARED
            memory_access.cpp)

find_library(log-lib log)
target_link_libraries(memorydebugger ${log-lib})
        """.strip())
    
    # Create memory_access.cpp
    memory_cpp_path = cpp_dir / "memory_access.cpp"
    
    with open(memory_cpp_path, 'w') as f:
        f.write("""
#include <jni.h>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <android/log.h>

#define LOGD(...) __android_log_print(ANDROID_LOG_DEBUG, "MemoryDebuggerNative", __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, "MemoryDebuggerNative", __VA_ARGS__)

extern "C" {
    // Note: These functions require root access to work on Android
    
    JNIEXPORT jstring JNICALL
    Java_com_memorydebugger_app_NativeMemoryAccess_listProcessesNative(JNIEnv *env, jobject /* this */) {
        LOGD("Listing processes from native code");
        
        std::string result = "[]";
        try {
            // On Linux/Android, we can read process list from /proc
            std::vector<std::string> processes;
            
            // This requires root on modern Android
            std::ifstream proc_dir("/proc");
            if (!proc_dir.is_open()) {
                LOGE("Failed to open /proc directory");
                return env->NewStringUTF(result.c_str());
            }
            
            std::string line;
            while (std::getline(proc_dir, line)) {
                // Check if line is a number (PID)
                if (std::all_of(line.begin(), line.end(), ::isdigit)) {
                    // Read process name from /proc/[pid]/comm
                    std::string comm_path = "/proc/" + line + "/comm";
                    std::ifstream comm_file(comm_path);
                    
                    if (comm_file.is_open()) {
                        std::string process_name;
                        std::getline(comm_file, process_name);
                        
                        // Add to JSON array
                        processes.push_back("{\\\"pid\\\":\\\"" + line + "\\\",\\\"name\\\":\\\"" + process_name + "\\\"}");
                    }
                }
            }
            
            // Create JSON array
            result = "[" + (processes.empty() ? "" : processes[0]);
            for (size_t i = 1; i < processes.size(); i++) {
                result += "," + processes[i];
            }
            result += "]";
            
        } catch (const std::exception& e) {
            LOGE("Exception in listProcessesNative: %s", e.what());
        }
        
        return env->NewStringUTF(result.c_str());
    }
    
    JNIEXPORT jstring JNICALL
    Java_com_memorydebugger_app_NativeMemoryAccess_readMemoryNative(
            JNIEnv *env, jobject /* this */,
            jstring j_pid, jstring j_address, jint size) {
        
        const char* pid_str = env->GetStringUTFChars(j_pid, nullptr);
        const char* address_str = env->GetStringUTFChars(j_address, nullptr);
        
        LOGD("Reading memory: PID %s, Address %s, Size %d", pid_str, address_str, size);
        
        std::string result = "null";
        try {
            // Parse address as hex
            unsigned long long address;
            std::stringstream ss;
            ss << std::hex << address_str;
            ss >> address;
            
            // Open process memory
            std::string mem_path = "/proc/" + std::string(pid_str) + "/mem";
            std::ifstream mem_file(mem_path, std::ios::binary);
            
            if (!mem_file.is_open()) {
                LOGE("Failed to open memory file: %s", mem_path.c_str());
            } else {
                // Seek to address
                mem_file.seekg(address);
                
                // Read memory
                std::vector<char> buffer(size);
                mem_file.read(buffer.data(), size);
                
                // Convert to hex string
                std::stringstream hex_ss;
                hex_ss << std::hex << std::setfill('0');
                for (int i = 0; i < size && mem_file.good(); i++) {
                    hex_ss << std::setw(2) << static_cast<int>(buffer[i] & 0xFF);
                }
                
                result = "\\\"" + hex_ss.str() + "\\\"";
            }
            
        } catch (const std::exception& e) {
            LOGE("Exception in readMemoryNative: %s", e.what());
        }
        
        env->ReleaseStringUTFChars(j_pid, pid_str);
        env->ReleaseStringUTFChars(j_address, address_str);
        
        return env->NewStringUTF(result.c_str());
    }
    
    JNIEXPORT jboolean JNICALL
    Java_com_memorydebugger_app_NativeMemoryAccess_writeMemoryNative(
            JNIEnv *env, jobject /* this */,
            jstring j_pid, jstring j_address, jstring j_value) {
        
        const char* pid_str = env->GetStringUTFChars(j_pid, nullptr);
        const char* address_str = env->GetStringUTFChars(j_address, nullptr);
        const char* value_str = env->GetStringUTFChars(j_value, nullptr);
        
        LOGD("Writing memory: PID %s, Address %s, Value %s", pid_str, address_str, value_str);
        
        bool success = false;
        try {
            // Parse address as hex
            unsigned long long address;
            std::stringstream addr_ss;
            addr_ss << std::hex << address_str;
            addr_ss >> address;
            
            // Parse hex value
            std::string value_hex = value_str;
            std::vector<char> buffer;
            
            for (size_t i = 0; i < value_hex.length(); i += 2) {
                std::string byte_str = value_hex.substr(i, 2);
                char byte = static_cast<char>(std::stoi(byte_str, nullptr, 16));
                buffer.push_back(byte);
            }
            
            // Open process memory
            std::string mem_path = "/proc/" + std::string(pid_str) + "/mem";
            std::ofstream mem_file(mem_path, std::ios::binary | std::ios::out);
            
            if (!mem_file.is_open()) {
                LOGE("Failed to open memory file for writing: %s", mem_path.c_str());
            } else {
                // Seek to address
                mem_file.seekp(address);
                
                // Write memory
                mem_file.write(buffer.data(), buffer.size());
                success = mem_file.good();
            }
            
        } catch (const std::exception& e) {
            LOGE("Exception in writeMemoryNative: %s", e.what());
        }
        
        env->ReleaseStringUTFChars(j_pid, pid_str);
        env->ReleaseStringUTFChars(j_address, address_str);
        env->ReleaseStringUTFChars(j_value, value_str);
        
        return success;
    }
}
        """.strip())
    
    # Create Java wrapper for native code
    java_dir = ANDROID_DIR / "app" / "src" / "main" / "java" / "com" / "memorydebugger" / "app"
    
    native_wrapper_path = java_dir / "NativeMemoryAccess.kt"
    
    with open(native_wrapper_path, 'w') as f:
        f.write("""
package com.memorydebugger.app

class NativeMemoryAccess {
    companion object {
        init {
            try {
                System.loadLibrary("memorydebugger")
            } catch (e: UnsatisfiedLinkError) {
                // Native library not available, may continue with limited functionality
            }
        }
    }
    
    // Native method declarations
    external fun listProcessesNative(): String
    
    external fun readMemoryNative(pid: String, address: String, size: Int): String
    
    external fun writeMemoryNative(pid: String, address: String, value: String): Boolean
    
    // Fallback methods using root shell commands via libsuperuser
    fun listProcessesRoot(): String {
        val processes = mutableListOf<Map<String, String>>()
        
        try {
            val commands = listOf("ps -ef")
            val output = eu.chainfire.libsuperuser.Shell.SU.run(commands)
            
            for (i in 1 until output.size) { // Skip header
                val parts = output[i].trim().split("\\s+".toRegex())
                if (parts.size >= 8) {
                    val pid = parts[1]
                    val name = parts[7]
                    processes.add(mapOf("pid" to pid, "name" to name))
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        
        return processes.toString()
    }
    
    fun readMemoryRoot(pid: String, address: String, size: Int): String {
        try {
            val commands = listOf(
                "su -c 'dd if=/proc/$pid/mem bs=1 count=$size skip=$address 2>/dev/null | xxd -p'"
            )
            val output = eu.chainfire.libsuperuser.Shell.SU.run(commands)
            
            if (output.isNotEmpty()) {
                return output.joinToString("")
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        
        return "null"
    }
    
    fun writeMemoryRoot(pid: String, address: String, value: String): Boolean {
        try {
            // This is complex to do with shell commands
            // For a real implementation, native code is preferred
            return false
        } catch (e: Exception) {
            e.printStackTrace()
        }
        
        return false
    }
    
    // Method to check if device is rooted
    fun isRooted(): Boolean {
        return eu.chainfire.libsuperuser.Shell.SU.available()
    }
}
        """.strip())
    
    # Update app gradle to include native code
    app_gradle_path = ANDROID_DIR / "app" / "build.gradle"
    
    try:
        with open(app_gradle_path, 'r') as f:
            gradle_content = f.read()
        
        # Add cmake configuration if not present
        if "externalNativeBuild" not in gradle_content:
            gradle_content = gradle_content.replace("android {", """android {
    externalNativeBuild {
        cmake {
            path "src/main/cpp/CMakeLists.txt"
        }
    }""")
        
        with open(app_gradle_path, 'w') as f:
            f.write(gradle_content)
    except Exception as e:
        print(f"Failed to update app gradle for native code: {e}")
    
    print("Native code files created successfully.")

def create_readme():
    """Create a README file for the Android version."""
    readme_path = ANDROID_DIR / "README.md"
    
    with open(readme_path, 'w') as f:
        f.write("""
# Memory Debugger Android

This is the Android version of Memory Debugger, which allows you to inspect and modify memory of processes on Android devices.

## Important Notes

1. **Root Access Required**: Most memory debugging features require root access on Android.
2. **Limited Functionality**: Some features available in the desktop version may be limited or unavailable on Android.
3. **Development Status**: This is an experimental version and may not work on all devices.

## Building the App

### Prerequisites
- Android Studio Arctic Fox (2020.3.1) or newer
- Android SDK 30 or newer
- Android NDK 21 or newer

### Steps to Build
1. Open the project in Android Studio
2. Sync the project with Gradle files
3. Build the project
4. Connect your Android device (with USB debugging enabled)
5. Run the app on your device

## Features

- View running processes on your device
- View memory regions of processes (requires root)
- Read memory values (requires root)
- Write memory values (requires root)

## Limitations

- Memory editing features require root access
- Not all features from the desktop version are available
- Performance may be slower than on desktop
- Some devices may have additional security measures that prevent memory access

## Troubleshooting

If you encounter issues:

1. Make sure your device is rooted
2. Grant superuser permissions to the app when prompted
3. Some newer Android versions have additional security measures that may prevent memory access even with root

## License

See the LICENSE file in the root directory for licensing information.
        """.strip())

def main():
    """Create the Android version of Memory Debugger."""
    print("Creating Android version of Memory Debugger...")
    
    # 1. Setup Android project structure
    if not setup_android_project():
        print("Creating manual project structure...")
        ANDROID_DIR.mkdir(exist_ok=True)
        (ANDROID_DIR / "app" / "src" / "main").mkdir(parents=True, exist_ok=True)
    
    # 2. Create WebView integration
    create_webview_integration()
    
    # 3. Prepare web assets
    prepare_web_assets()
    
    # 4. Create Gradle build files
    create_gradle_files()
    
    # 5. Create native code for memory access
    create_native_code()
    
    # 6. Create README
    create_readme()
    
    print("Android version setup completed!")
    print("To build the Android app:")
    print("1. Open the 'android' directory in Android Studio")
    print("2. Allow Gradle sync to complete")
    print("3. Build the project")
    print("4. Run on your Android device")
    
    print("\nNote: Most memory features require root access on Android")

if __name__ == "__main__":
    main()