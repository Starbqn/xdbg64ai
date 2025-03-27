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
                        processes.push_back("{\"pid\":\"" + line + "\",\"name\":\"" + process_name + "\"}");
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
                
                result = "\"" + hex_ss.str() + "\"";
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