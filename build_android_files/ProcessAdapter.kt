package com.memorydebugger.app

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class ProcessAdapter(
    private var processes: List<MainActivity.ProcessInfo>,
    private val onProcessSelected: (MainActivity.ProcessInfo) -> Unit
) : RecyclerView.Adapter<ProcessAdapter.ProcessViewHolder>() {

    class ProcessViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val processName: TextView = view.findViewById(R.id.tvProcessName)
        val processPid: TextView = view.findViewById(R.id.tvProcessPid)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ProcessViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_process, parent, false)
        return ProcessViewHolder(view)
    }

    override fun onBindViewHolder(holder: ProcessViewHolder, position: Int) {
        val process = processes[position]
        holder.processName.text = process.name
        holder.processPid.text = "PID: ${process.pid}"
        
        holder.itemView.setOnClickListener {
            onProcessSelected(process)
        }
    }

    override fun getItemCount() = processes.size

    fun updateProcesses(newProcesses: List<MainActivity.ProcessInfo>) {
        processes = newProcesses
        notifyDataSetChanged()
    }
}