"""
OPC-UA Client Service for industrial data ingestion
"""
import asyncio
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from asyncua import Client, ua
from asyncua.common import Node

from app.utils.logger import setup_logging

logger = setup_logging()


class OPCUAClient:
    """OPC-UA client for receiving industrial data"""
    
    def __init__(
        self,
        endpoint_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.endpoint_url = endpoint_url
        self.username = username
        self.password = password
        
        self.client: Optional[Client] = None
        self.is_connected = False
        self.subscriptions: Dict[str, Any] = {}
        self.monitored_nodes: List[Node] = []
        self.data_callback: Optional[Callable] = None
    
    async def connect(self):
        """Connect to OPC-UA server"""
        try:
            self.client = Client(url=self.endpoint_url)
            
            # Set credentials if provided
            if self.username and self.password:
                self.client.set_user(self.username)
                self.client.set_password(self.password)
            
            # Connect
            await self.client.connect()
            self.is_connected = True
            
            logger.info("OPC-UA client connected", endpoint=self.endpoint_url)
            
        except Exception as e:
            logger.error("Failed to connect to OPC-UA server", error=str(e), endpoint=self.endpoint_url)
            raise
    
    async def disconnect(self):
        """Disconnect from OPC-UA server"""
        if self.client and self.is_connected:
            # Unsubscribe from all subscriptions
            for sub_id, subscription in self.subscriptions.items():
                try:
                    await subscription.delete()
                except Exception as e:
                    logger.warning("Error deleting subscription", subscription_id=sub_id, error=str(e))
            
            await self.client.disconnect()
            self.is_connected = False
            logger.info("OPC-UA client disconnected")
    
    async def browse_nodes(self, node_id: str = "i=85") -> List[Dict[str, Any]]:
        """Browse nodes in OPC-UA server"""
        if not self.client or not self.is_connected:
            raise ConnectionError("OPC-UA client not connected")
        
        try:
            node = self.client.get_node(node_id)
            children = await node.get_children()
            
            nodes_info = []
            for child in children:
                try:
                    display_name = await child.read_display_name()
                    node_class = await child.read_node_class()
                    
                    nodes_info.append({
                        'node_id': str(child.nodeid),
                        'display_name': display_name.Text,
                        'node_class': str(node_class),
                    })
                except Exception as e:
                    logger.warning("Error reading node", node_id=str(child.nodeid), error=str(e))
            
            return nodes_info
            
        except Exception as e:
            logger.error("Error browsing nodes", error=str(e))
            raise
    
    async def read_node_value(self, node_id: str) -> Any:
        """Read value from a specific node"""
        if not self.client or not self.is_connected:
            raise ConnectionError("OPC-UA client not connected")
        
        try:
            node = self.client.get_node(node_id)
            value = await node.read_value()
            return value
        except Exception as e:
            logger.error("Error reading node value", node_id=node_id, error=str(e))
            raise
    
    async def monitor_nodes(
        self,
        node_ids: List[str],
        sampling_interval: int = 1000,
        callback: Optional[Callable] = None
    ):
        """Monitor multiple nodes for value changes"""
        if not self.client or not self.is_connected:
            raise ConnectionError("OPC-UA client not connected")
        
        try:
            # Create subscription
            subscription = await self.client.create_subscription(
                sampling_interval,
                self._handle_data_change
            )
            
            # Get nodes
            nodes = [self.client.get_node(node_id) for node_id in node_ids]
            self.monitored_nodes.extend(nodes)
            
            # Set callback
            if callback:
                self.data_callback = callback
            
            # Create monitored items
            handles = await subscription.subscribe_data_change(nodes)
            
            subscription_id = f"sub_{datetime.now().timestamp()}"
            self.subscriptions[subscription_id] = {
                'subscription': subscription,
                'handles': handles,
                'nodes': nodes,
            }
            
            logger.info("Monitoring nodes", node_count=len(node_ids), subscription_id=subscription_id)
            
            return subscription_id
            
        except Exception as e:
            logger.error("Error setting up node monitoring", error=str(e))
            raise
    
    async def _handle_data_change(self, node: Node, val, data):
        """Handle data change notification from OPC-UA"""
        try:
            node_id = str(node.nodeid)
            display_name = await node.read_display_name()
            
            data_dict = {
                'node_id': node_id,
                'display_name': display_name.Text,
                'value': val,
                'source_timestamp': data.SourceTimestamp.isoformat() if data.SourceTimestamp else None,
                'status_code': str(data.StatusCode),
                '_metadata': {
                    'source': 'opcua',
                    'timestamp': datetime.utcnow().isoformat(),
                }
            }
            
            # Call callback if set
            if self.data_callback:
                self.data_callback(data_dict)
            else:
                logger.debug("OPC-UA data received", node_id=node_id, value=val)
                
        except Exception as e:
            logger.error("Error handling OPC-UA data change", error=str(e))
    
    async def write_node_value(self, node_id: str, value: Any, data_type: Optional[ua.VariantType] = None):
        """Write value to a node"""
        if not self.client or not self.is_connected:
            raise ConnectionError("OPC-UA client not connected")
        
        try:
            node = self.client.get_node(node_id)
            
            if data_type:
                variant = ua.Variant(value, data_type)
                await node.write_value(variant)
            else:
                await node.write_value(value)
            
            logger.info("Wrote value to node", node_id=node_id, value=value)
            
        except Exception as e:
            logger.error("Error writing node value", node_id=node_id, error=str(e))
            raise

