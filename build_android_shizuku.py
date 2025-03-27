#!/usr/bin/env python3
"""
Build script for Memory Debugger Android app with Shizuku support.
This script prepares the Android application structure and files.
"""

import os
import sys
import shutil
import subprocess
import re
from pathlib import Path
import tempfile
import json
import zipfile

# Define the base directories
CURRENT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
ANDROID_DIR = CURRENT_DIR / "android_app"
BUILD_FILES_DIR = CURRENT_DIR / "build_android_files"
APK_OUTPUT_DIR = CURRENT_DIR / "builds"

def setup_android_project():
    """Set up the Android project structure."""
    print("Setting up Android project structure...")
    
    # Create the main directories
    project_dirs = [
        ANDROID_DIR,
        ANDROID_DIR / "app",
        ANDROID_DIR / "app" / "src",
        ANDROID_DIR / "app" / "src" / "main",
        ANDROID_DIR / "app" / "src" / "main" / "java",
        ANDROID_DIR / "app" / "src" / "main" / "java" / "com" / "memorydebugger" / "app",
        ANDROID_DIR / "app" / "src" / "main" / "res",
        ANDROID_DIR / "app" / "src" / "main" / "res" / "layout",
        ANDROID_DIR / "app" / "src" / "main" / "res" / "values",
        ANDROID_DIR / "app" / "src" / "main" / "res" / "mipmap-hdpi",
        ANDROID_DIR / "app" / "src" / "main" / "res" / "mipmap-mdpi",
        ANDROID_DIR / "app" / "src" / "main" / "res" / "mipmap-xhdpi",
        ANDROID_DIR / "app" / "src" / "main" / "res" / "mipmap-xxhdpi",
        ANDROID_DIR / "app" / "src" / "main" / "res" / "mipmap-xxxhdpi",
        ANDROID_DIR / "app" / "src" / "main" / "assets",
        ANDROID_DIR / "gradle" / "wrapper",
    ]
    
    for dir_path in project_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("Android project structure created successfully.")

def copy_build_files():
    """Copy the build files to the appropriate directories."""
    print("Copying build files...")
    
    # Java/Kotlin files
    java_dir = ANDROID_DIR / "app" / "src" / "main" / "java" / "com" / "memorydebugger" / "app"
    java_src_files = [
        "MainActivity.kt",
        "ProcessAdapter.kt",
        "WebViewActivity.kt",
        "WebAppInterface.kt",
        "ShizukuMemoryAccess.kt",
    ]
    
    for file_name in java_src_files:
        src_path = BUILD_FILES_DIR / file_name
        if src_path.exists():
            shutil.copy(src_path, java_dir / file_name)
            print(f"Copied {file_name} to {java_dir}")
    
    # Layout files
    layout_dir = ANDROID_DIR / "app" / "src" / "main" / "res" / "layout"
    layout_files = [
        "activity_main.xml",
        "activity_webview.xml",
        "item_process.xml",
    ]
    
    for file_name in layout_files:
        src_path = BUILD_FILES_DIR / file_name
        if src_path.exists():
            shutil.copy(src_path, layout_dir / file_name)
            print(f"Copied {file_name} to {layout_dir}")
    
    # Values files
    values_dir = ANDROID_DIR / "app" / "src" / "main" / "res" / "values"
    values_files = [
        "colors.xml",
        "strings.xml",
        "themes.xml",
    ]
    
    for file_name in values_files:
        src_path = BUILD_FILES_DIR / file_name
        if src_path.exists():
            shutil.copy(src_path, values_dir / file_name)
            print(f"Copied {file_name} to {values_dir}")
    
    # AndroidManifest.xml
    manifest_src = BUILD_FILES_DIR / "AndroidManifest.xml"
    if manifest_src.exists():
        shutil.copy(manifest_src, ANDROID_DIR / "app" / "src" / "main" / "AndroidManifest.xml")
        print(f"Copied AndroidManifest.xml to {ANDROID_DIR / 'app' / 'src' / 'main'}")
    
    # Copy web assets
    assets_dir = ANDROID_DIR / "app" / "src" / "main" / "assets"
    src_static_dir = CURRENT_DIR / "static"
    src_templates_dir = CURRENT_DIR / "templates"
    
    if src_static_dir.exists():
        for file in src_static_dir.glob("**/*"):
            if file.is_file():
                dest_file = assets_dir / file.relative_to(src_static_dir)
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(file, dest_file)
                print(f"Copied {file} to {dest_file}")
    
    if src_templates_dir.exists():
        for file in src_templates_dir.glob("**/*.html"):
            if file.is_file():
                dest_file = assets_dir / file.name
                shutil.copy(file, dest_file)
                print(f"Copied {file} to {dest_file}")
    
    # Also create a basic index.html if none exists
    index_html_path = assets_dir / "index.html"
    if not index_html_path.exists():
        with open(index_html_path, 'w') as f:
            f.write("""<!DOCTYPE html>
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
            background-color: #f8f9fa;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
        }
        .card {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .btn {
            background-color: #6200ee;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
        }
        .btn:disabled {
            background-color: #cccccc;
        }
        input, select {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 100%;
            margin-bottom: 10px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Memory Debugger</h1>
        
        <div class="card">
            <h2>Access Method</h2>
            <label>
                <input type="radio" name="accessMethod" value="shizuku" checked> Shizuku
            </label>
            <label>
                <input type="radio" name="accessMethod" value="root"> Root
            </label>
            <div id="statusText">Checking access method...</div>
            <button id="checkPermissionBtn" class="btn">Check/Request Permissions</button>
        </div>
        
        <div class="card">
            <h2>Processes</h2>
            <div id="processList" style="max-height: 300px; overflow-y: auto; margin-bottom: 10px;">
                <p>No processes loaded.</p>
            </div>
            <button id="refreshProcessesBtn" class="btn">Refresh Process List</button>
        </div>
        
        <div id="memoryCard" class="card" style="display: none;">
            <h2>Memory Operations</h2>
            <div id="selectedProcess">Selected process: None</div>
            
            <label for="memoryAddress">Memory Address (hex)</label>
            <input type="text" id="memoryAddress" placeholder="Enter memory address">
            
            <label for="memorySize">Size (bytes)</label>
            <input type="number" id="memorySize" value="8" min="1">
            
            <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                <button id="readMemoryBtn" class="btn">Read</button>
                <button id="writeMemoryBtn" class="btn">Write</button>
            </div>
            
            <label for="memoryValue">Memory Value (hex)</label>
            <input type="text" id="memoryValue" placeholder="Memory value in hex">
            
            <button id="viewMemoryRegionsBtn" class="btn" style="margin-top: 10px;">View Memory Map</button>
        </div>
    </div>

    <script>
        // Check if Android interface is available
        const isAndroidApp = !!window.Android;
        
        // Selected process
        let selectedProcess = null;
        let accessMethod = 'shizuku';
        
        // Elements
        const statusText = document.getElementById('statusText');
        const checkPermissionBtn = document.getElementById('checkPermissionBtn');
        const refreshProcessesBtn = document.getElementById('refreshProcessesBtn');
        const processList = document.getElementById('processList');
        const memoryCard = document.getElementById('memoryCard');
        const selectedProcessText = document.getElementById('selectedProcess');
        const memoryAddress = document.getElementById('memoryAddress');
        const memorySize = document.getElementById('memorySize');
        const memoryValue = document.getElementById('memoryValue');
        const readMemoryBtn = document.getElementById('readMemoryBtn');
        const writeMemoryBtn = document.getElementById('writeMemoryBtn');
        const viewMemoryRegionsBtn = document.getElementById('viewMemoryRegionsBtn');
        
        // Radio buttons for access method
        document.querySelectorAll('input[name="accessMethod"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                accessMethod = e.target.value;
                updateStatus();
            });
        });
        
        // Check permission button
        checkPermissionBtn.addEventListener('click', () => {
            if (!isAndroidApp) {
                showMessage('This feature is only available in the Android app');
                return;
            }
            
            if (accessMethod === 'shizuku') {
                const result = window.Android.requestShizukuPermission();
                updateStatus();
            } else {
                // Root doesn't need to request permission
                updateStatus();
            }
        });
        
        // Refresh processes button
        refreshProcessesBtn.addEventListener('click', loadProcesses);
        
        // Read memory button
        readMemoryBtn.addEventListener('click', () => {
            if (!selectedProcess) {
                showMessage('No process selected');
                return;
            }
            
            const address = memoryAddress.value;
            const size = parseInt(memorySize.value);
            
            if (!address || isNaN(size)) {
                showMessage('Please enter valid address and size');
                return;
            }
            
            try {
                let result;
                if (accessMethod === 'shizuku') {
                    result = window.Android.readMemoryShizuku(selectedProcess.pid, address, size);
                } else {
                    result = window.Android.readMemoryRoot(selectedProcess.pid, address, size);
                }
                
                if (result) {
                    memoryValue.value = result;
                } else {
                    showMessage('Failed to read memory');
                }
            } catch (e) {
                showMessage('Error: ' + e.message);
            }
        });
        
        // Write memory button
        writeMemoryBtn.addEventListener('click', () => {
            if (!selectedProcess) {
                showMessage('No process selected');
                return;
            }
            
            const address = memoryAddress.value;
            const value = memoryValue.value;
            
            if (!address || !value) {
                showMessage('Please enter valid address and value');
                return;
            }
            
            try {
                let result;
                if (accessMethod === 'shizuku') {
                    result = window.Android.writeMemoryShizuku(selectedProcess.pid, address, value);
                } else {
                    result = window.Android.writeMemoryRoot(selectedProcess.pid, address, value);
                }
                
                if (result) {
                    showMessage('Memory written successfully');
                } else {
                    showMessage('Failed to write memory');
                }
            } catch (e) {
                showMessage('Error: ' + e.message);
            }
        });
        
        // View memory regions button
        viewMemoryRegionsBtn.addEventListener('click', () => {
            if (!selectedProcess) {
                showMessage('No process selected');
                return;
            }
            
            if (accessMethod === 'shizuku') {
                try {
                    const regionsJson = window.Android.getMemoryRegionsShizuku(selectedProcess.pid);
                    const regions = JSON.parse(regionsJson);
                    
                    if (regions.length === 0) {
                        showMessage('No memory regions found');
                        return;
                    }
                    
                    // In a real app, this would show a proper modal dialog
                    alert('Found ' + regions.length + ' memory regions. First region: ' + 
                          regions[0].baseAddress + '-' + regions[0].endAddress + 
                          ' [' + regions[0].permissions + '] ' + 
                          (regions[0].path || 'anonymous'));
                    
                } catch (e) {
                    showMessage('Error getting memory regions: ' + e.message);
                }
            } else {
                showMessage('Memory regions view not implemented for root access');
            }
        });
        
        // Update status on load
        updateStatus();
        
        // Load processes on startup if possible
        if (isAndroidApp) {
            loadProcesses();
        }
        
        // Helper functions
        function updateStatus() {
            if (!isAndroidApp) {
                statusText.textContent = 'Status: Running in browser, Android features unavailable';
                return;
            }
            
            if (accessMethod === 'shizuku') {
                if (window.Android.isShizukuAvailable()) {
                    statusText.textContent = 'Status: Shizuku is available, checking permission...';
                    const hasPermission = window.Android.requestShizukuPermission();
                    if (hasPermission) {
                        statusText.textContent = 'Status: Shizuku is available and permitted';
                    } else {
                        statusText.textContent = 'Status: Shizuku is available but not permitted';
                    }
                } else {
                    statusText.textContent = 'Status: Shizuku is not available';
                }
            } else {
                if (window.Android.isRooted()) {
                    statusText.textContent = 'Status: Root access is available';
                } else {
                    statusText.textContent = 'Status: Root access is not available';
                }
            }
        }
        
        function loadProcesses() {
            if (!isAndroidApp) {
                showMessage('This feature is only available in the Android app');
                return;
            }
            
            try {
                let processesJson;
                
                if (accessMethod === 'shizuku') {
                    processesJson = window.Android.listProcessesShizuku();
                } else {
                    processesJson = window.Android.listProcessesRoot();
                }
                
                const processes = JSON.parse(processesJson);
                
                if (processes.length === 0) {
                    processList.innerHTML = '<p>No processes found.</p>';
                    return;
                }
                
                processList.innerHTML = '';
                processes.forEach(process => {
                    const div = document.createElement('div');
                    div.className = 'process-item';
                    div.style.padding = '8px';
                    div.style.border = '1px solid #eee';
                    div.style.borderRadius = '4px';
                    div.style.marginBottom = '4px';
                    div.style.cursor = 'pointer';
                    
                    div.innerHTML = `
                        <div><strong>${process.name}</strong></div>
                        <div>PID: ${process.pid}</div>
                    `;
                    
                    div.addEventListener('click', () => {
                        selectedProcess = process;
                        selectedProcessText.textContent = `Selected process: ${process.name} (PID: ${process.pid})`;
                        memoryCard.style.display = 'block';
                        
                        // Highlight the selected process
                        document.querySelectorAll('.process-item').forEach(item => {
                            item.style.backgroundColor = '';
                        });
                        div.style.backgroundColor = '#e8f0fe';
                    });
                    
                    processList.appendChild(div);
                });
            } catch (e) {
                processList.innerHTML = '<p>Error loading processes: ' + e.message + '</p>';
            }
        }
        
        function showMessage(message) {
            if (isAndroidApp) {
                window.Android.showToast(message);
            } else {
                alert(message);
            }
        }
    </script>
</body>
</html>""")
        print(f"Created index.html in {assets_dir}")
    
    print("Build files copied successfully.")

def create_gradle_files():
    """Create Gradle build files for the Android project."""
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
    compileSdk 33
    
    defaultConfig {
        applicationId "com.memorydebugger.app"
        minSdk 24
        targetSdk 33
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
    
    externalNativeBuild {
        cmake {
            path "src/main/cpp/CMakeLists.txt"
        }
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.10.1'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'androidx.recyclerview:recyclerview:1.3.0'
    implementation 'androidx.cardview:cardview:1.0.0'
    implementation 'androidx.webkit:webkit:1.6.0'
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
    
    # Create gradle wrapper files
    gradle_wrapper_dir = ANDROID_DIR / "gradle" / "wrapper"
    gradle_wrapper_dir.mkdir(parents=True, exist_ok=True)
    
    gradle_wrapper_properties_path = gradle_wrapper_dir / "gradle-wrapper.properties"
    gradle_wrapper_properties_content = """
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.0-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
"""
    
    with open(gradle_wrapper_properties_path, 'w') as f:
        f.write(gradle_wrapper_properties_content.strip())
    
    # Create gradlew and gradlew.bat scripts
    gradlew_path = ANDROID_DIR / "gradlew"
    with open(gradlew_path, 'w') as f:
        f.write("#!/usr/bin/env sh\n\n# Gradle wrapper script for Unix")
    
    gradlew_bat_path = ANDROID_DIR / "gradlew.bat"
    with open(gradlew_bat_path, 'w') as f:
        f.write("@rem Gradle wrapper script for Windows\n")
    
    # Make gradlew executable
    os.chmod(gradlew_path, 0o755)
    
    print("Gradle build files created successfully.")

def create_native_code():
    """Create native code implementation for memory access."""
    print("Creating native code files...")
    
    # Create directory for native code
    cpp_dir = ANDROID_DIR / "app" / "src" / "main" / "cpp"
    cpp_dir.mkdir(parents=True, exist_ok=True)
    
    # Create CMakeLists.txt
    cmake_path = cpp_dir / "CMakeLists.txt"
    cmake_content = """
cmake_minimum_required(VERSION 3.18.1)
project(memorydebugger)

add_library(memorydebugger SHARED
            memory_access.cpp)

find_library(log-lib log)
target_link_libraries(memorydebugger ${log-lib})
"""
    
    with open(cmake_path, 'w') as f:
        f.write(cmake_content.strip())
    
    # Create memory_access.cpp
    memory_cpp_path = cpp_dir / "memory_access.cpp"
    memory_cpp_content = """
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
"""
    
    with open(memory_cpp_path, 'w') as f:
        f.write(memory_cpp_content.strip())
    
    print("Native code files created successfully.")

def copy_icon():
    """Copy icon files to the Android project."""
    print("Copying icon files...")
    
    # Use the existing icon if available
    icon_path = CURRENT_DIR / "generated-icon.png"
    if not icon_path.exists():
        print("Icon not found, skipping icon copy.")
        return
    
    from PIL import Image
    import io
    
    # Dictionary of mipmap directories and their sizes
    mipmap_sizes = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192
    }
    
    try:
        # Open the source icon
        img = Image.open(icon_path)
        
        # Resize and save the icon for each mipmap directory
        for mipmap_dir, size in mipmap_sizes.items():
            dest_dir = ANDROID_DIR / "app" / "src" / "main" / "res" / mipmap_dir
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Resize the image
            resized_img = img.resize((size, size), Image.LANCZOS)
            
            # Save as ic_launcher.png
            resized_img.save(dest_dir / "ic_launcher.png")
            
            # Save as ic_launcher_round.png (same for simplicity)
            resized_img.save(dest_dir / "ic_launcher_round.png")
        
        print("Icon files copied successfully.")
    except Exception as e:
        print(f"Error copying icon: {e}")
        print("Skipping icon copy, app will use default Android icon.")

def create_dummy_apk():
    """Create a dummy APK file for development purposes."""
    print("Creating dummy APK file...")
    
    # Ensure the output directory exists
    APK_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create a dummy APK file
    apk_path = APK_OUTPUT_DIR / "MemoryDebugger-dev.apk"
    
    # Create a simple zip file with the Android structure
    with zipfile.ZipFile(apk_path, 'w') as zipf:
        # Add a META-INF folder with a MANIFEST.MF
        manifest_content = "Manifest-Version: 1.0\nCreated-By: Memory Debugger Build Script\n"
        zipf.writestr("META-INF/MANIFEST.MF", manifest_content)
        
        # Add a simple dex file placeholder
        zipf.writestr("classes.dex", "This is a placeholder for DEX file")
        
        # Add AndroidManifest.xml placeholder
        zipf.writestr("AndroidManifest.xml", "This is a placeholder for AndroidManifest.xml")
        
        # Add a resources placeholder
        zipf.writestr("resources.arsc", "This is a placeholder for resources.arsc")
    
    print(f"Dummy APK created at: {apk_path}")
    
    # Create a readme file explaining how to build the real APK
    readme_path = APK_OUTPUT_DIR / "HOW_TO_BUILD_APK.md"
    readme_content = """# How to Build the Memory Debugger APK

This is a placeholder APK file. To build the actual APK:

1. Install Android Studio from [developer.android.com](https://developer.android.com/studio)
2. Open the 'android_app' folder in Android Studio
3. Wait for Gradle sync to complete
4. Click on Build > Build Bundle(s) / APK(s) > Build APK(s)
5. The APK will be generated in 'android_app/app/build/outputs/apk/debug/'

## Requirements

- Android Studio Arctic Fox (2020.3.1) or newer
- Android SDK 30 or newer
- Android NDK 21 or newer

## Features in the Full APK

- List running processes on Android devices
- Read and write memory of processes (requires Shizuku or root)
- View memory maps of processes
- Web interface for advanced features
"""
    
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"Instructions created at: {readme_path}")

def create_readme():
    """Create a README file for Shizuku integration."""
    print("Creating README file...")
    
    readme_path = CURRENT_DIR / "ANDROID_SHIZUKU_README.md"
    readme_content = """# Memory Debugger with Shizuku Integration

## Overview

This version of Memory Debugger includes Shizuku integration for Android, allowing memory debugging without requiring full root access. Shizuku provides a more controlled and secure way to access process memory while maintaining most of the functionality available in the root-only version.

## What is Shizuku?

Shizuku is a tool that grants apps the ability to run commands with elevated permissions, similar to `adb shell`. It works in two modes:

1. **ADB Mode**: Works on any Android device with USB debugging enabled. Users connect their device to a computer once to set up Shizuku.
2. **Root Mode**: For rooted devices, Shizuku can start automatically without requiring a computer.

## Features Enabled by Shizuku

- List all running processes on the device
- Read memory from other app processes
- Write memory to other app processes (with limitations)
- View memory maps and regions
- All done without requiring full root access

## Requirements

- Android 8.0 (API 26) or higher
- Shizuku app installed from [Google Play](https://play.google.com/store/apps/details?id=moe.shizuku.privileged.api) or [GitHub](https://github.com/RikkaApps/Shizuku/releases)
- Either:
  - One-time USB debugging setup with a computer, or
  - A rooted device

## Setup Instructions

### Setting up Shizuku with ADB (non-rooted devices)

1. Install the Shizuku app from Google Play Store
2. Enable Developer Options on your device:
   - Go to Settings > About phone
   - Tap "Build number" 7 times
3. Enable USB debugging in Developer Options
4. Connect your device to a computer
5. Set up Shizuku by following the app's instructions
6. Once set up, you can disconnect from the computer

### Setting up Shizuku with Root

1. Install the Shizuku app from Google Play Store
2. Open the app and select "Start with root"
3. Grant root access when prompted

## Using Memory Debugger with Shizuku

1. Launch Memory Debugger
2. Select "Shizuku" as the access method
3. Tap "Check/Request Permissions"
4. Grant Shizuku permissions when prompted
5. Now you can browse processes and perform memory operations

## Limitations

- Some deeply protected system processes may still be inaccessible
- Performance may be slower than with direct root access
- On some devices, you may need to restart Shizuku after rebooting

## Troubleshooting

- If Memory Debugger can't connect to Shizuku, try restarting the Shizuku app
- If you get permission errors, make sure you've granted Shizuku permission to Memory Debugger
- On some devices, the ADB-based Shizuku may stop working after a system update, requiring reconnection to a computer

## Safety Notes

While Shizuku is safer than full root access, it still provides elevated permissions that could potentially be misused. Only use Memory Debugger on apps you own or have permission to modify.

## Building the App

See the HOW_TO_BUILD_APK.md file in the builds directory for instructions on building the app from source.
"""
    
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"README created at: {readme_path}")

def update_android_process_connector():
    """Update the android_process_connector.py with Shizuku support."""
    print("Updating Android Process Connector...")
    
    # Check if the file exists
    connector_path = CURRENT_DIR / "android_process_connector.py"
    if not connector_path.exists():
        print("Warning: android_process_connector.py not found, cannot update.")
        return
    
    # Read the existing file
    with open(connector_path, 'r') as f:
        connector_content = f.read()
    
    # Add Shizuku support if not already present
    if "shizuku_support" not in connector_content.lower():
        shizuku_additions = """
    def use_shizuku(self) -> bool:
        \"\"\"Configure to use Shizuku instead of direct root\"\"\"
        self.using_shizuku = True
        return True
        
    def is_shizuku_available(self) -> bool:
        \"\"\"Check if Shizuku is available on the device\"\"\"
        if not self.is_android_connected():
            return False
            
        # Use adb to check if Shizuku is installed
        result = subprocess.run(
            ["adb", "shell", "pm", "list", "packages", "moe.shizuku.privileged.api"],
            capture_output=True,
            text=True
        )
        
        return "moe.shizuku.privileged.api" in result.stdout
"""
        
        # Find the class definition
        class_def_match = re.search(r"class AndroidProcessConnector:", connector_content)
        if class_def_match:
            # Find the end of the __init__ method
            init_end_match = re.search(r"def __init__\(self\):.*?(\n\s+\w+|\n\w+)", connector_content, re.DOTALL)
            if init_end_match:
                # Update the __init__ method
                init_update = "def __init__(self):\n        \"\"\"Android-specific implementation to interface with Android app\"\"\"\n        self.adb_path = shutil.which('adb')\n        self.attached_pid = None\n        self.using_shizuku = False  # New flag for Shizuku support"
                
                connector_content = connector_content.replace(
                    connector_content[class_def_match.end():init_end_match.end()],
                    "\n    " + init_update
                )
            
            # Add the new methods at the end of the class
            class_end_match = re.search(r"def is_running_on_android\(\)", connector_content)
            if class_end_match:
                connector_content = connector_content[:class_end_match.start()] + shizuku_additions + "\n\n" + connector_content[class_end_match.start():]
                
                # Write the updated content back to the file
                with open(connector_path, 'w') as f:
                    f.write(connector_content)
                
                print("Updated android_process_connector.py with Shizuku support.")
            else:
                print("Could not locate the end of the AndroidProcessConnector class.")
        else:
            print("Could not locate the AndroidProcessConnector class definition.")

def main():
    """Main function to build the Android app with Shizuku support."""
    print("Building Android app with Shizuku support...")
    
    # Set up the basic project structure
    setup_android_project()
    
    # Create the Gradle build files
    create_gradle_files()
    
    # Copy all the build files
    copy_build_files()
    
    # Create native code
    create_native_code()
    
    # Copy the icon
    copy_icon()
    
    # Create dummy APK and instructions
    create_dummy_apk()
    
    # Create README
    create_readme()
    
    # Update Android Process Connector
    update_android_process_connector()
    
    print("Build completed successfully!")
    print(f"Android project created in: {ANDROID_DIR}")
    print(f"Dummy APK and build instructions in: {APK_OUTPUT_DIR}")
    print("To build the actual APK, open the project in Android Studio and build from there.")
    print("For more information, see the ANDROID_SHIZUKU_README.md file.")

if __name__ == "__main__":
    main()