import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
import time

@dataclass
class NodeStatus:
    node_id: str
    last_heartbeat: float
    cpu_load: float
    memory_usage: float
    active_tasks: int

class Orchestrator:
    def __init__(self):
        self.nodes: Dict[str, NodeStatus] = {}
        self.task_queue: List[dict] = []
        self.health_check_interval = 10  # seconds
        self.node_timeout = 30  # seconds

    async def register_node(self, node_id: str) -> bool:
        if node_id not in self.nodes:
            self.nodes[node_id] = NodeStatus(
                node_id=node_id,
                last_heartbeat=time.time(),
                cpu_load=0.0,
                memory_usage=0.0,
                active_tasks=0
            )
            print(f'Node {node_id} registered successfully')
            return True
        return False

    async def update_node_status(self, node_id: str, cpu_load: float, memory_usage: float) -> None:
        if node_id in self.nodes:
            self.nodes[node_id].last_heartbeat = time.time()
            self.nodes[node_id].cpu_load = cpu_load
            self.nodes[node_id].memory_usage = memory_usage

    async def get_optimal_node(self) -> Optional[str]:
        available_nodes = [
            (node_id, status) for node_id, status in self.nodes.items()
            if time.time() - status.last_heartbeat < self.node_timeout
        ]

        if not available_nodes:
            return None

        # Score nodes based on load and resource usage
        scored_nodes = [
            (node_id, status.cpu_load * 0.6 + status.memory_usage * 0.4 + status.active_tasks * 0.2)
            for node_id, status in available_nodes
        ]

        # Return node with lowest score (least loaded)
        return min(scored_nodes, key=lambda x: x[1])[0]

    async def health_monitor(self):
        while True:
            current_time = time.time()
            dead_nodes = [
                node_id for node_id, status in self.nodes.items()
                if current_time - status.last_heartbeat > self.node_timeout
            ]

            for node_id in dead_nodes:
                print(f'Node {node_id} timed out, removing from cluster')
                del self.nodes[node_id]

            # Rebalance tasks from dead nodes
            await self.rebalance_tasks(dead_nodes)
            await asyncio.sleep(self.health_check_interval)

    async def rebalance_tasks(self, failed_nodes: List[str]) -> None:
        tasks_to_reassign = [
            task for task in self.task_queue
            if task.get('assigned_node') in failed_nodes
        ]

        for task in tasks_to_reassign:
            optimal_node = await self.get_optimal_node()
            if optimal_node:
                task['assigned_node'] = optimal_node
                self.nodes[optimal_node].active_tasks += 1

    async def assign_task(self, task: dict) -> Optional[str]:
        optimal_node = await self.get_optimal_node()
        if optimal_node:
            task['assigned_node'] = optimal_node
            self.task_queue.append(task)
            self.nodes[optimal_node].active_tasks += 1
            return optimal_node
        return None

    def get_cluster_status(self) -> Dict:
        return {
            'total_nodes': len(self.nodes),
            'active_nodes': sum(1 for status in self.nodes.values()
                              if time.time() - status.last_heartbeat < self.node_timeout),
            'total_tasks': len(self.task_queue),
            'nodes': {
                node_id: {
                    'cpu_load': status.cpu_load,
                    'memory_usage': status.memory_usage,
                    'active_tasks': status.active_tasks,
                    'last_heartbeat': status.last_heartbeat
                } for node_id, status in self.nodes.items()
            }
        }
