"""OpenThread Border Router (OTBR) REST API Client.

This module provides a client for interacting with the OTBR REST API.
Default endpoint: http://{host}:8081
"""

from typing import Any, Dict, Optional
import requests


class OTBRClient:
    """Client for OpenThread Border Router REST API."""

    def __init__(self, host: str = "localhost", port: int = 8081, timeout: int = 10):
        """Initialize OTBR client.
        
        Args:
            host: The host address of the OTBR instance
            port: The port number (default: 8081)
            timeout: Request timeout in seconds
        """
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to OTBR API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            timeout=self.timeout,
            **kwargs
        )
        response.raise_for_status()
        return response.json() if response.text else {}

    # Node Information
    def get_node_info(self) -> Dict[str, Any]:
        """Get information about the Thread network node.
        
        Returns:
            Dictionary containing node information
        """
        return self._request("GET", "/node")

    def get_node_state(self) -> Dict[str, Any]:
        """Get the current state of the node.
        
        Returns:
            Dictionary containing node state
        """
        return self._request("GET", "/node/state")

    def get_node_ext_address(self) -> Dict[str, Any]:
        """Get the extended address of the node.
        
        Returns:
            Dictionary containing extended address
        """
        return self._request("GET", "/node/ext-address")

    def get_node_rloc16(self) -> Dict[str, Any]:
        """Get the RLOC16 (Router/Child Locator) of the node.
        
        Returns:
            Dictionary containing RLOC16
        """
        return self._request("GET", "/node/rloc16")

    # Network Information
    def get_network_name(self) -> Dict[str, Any]:
        """Get the Thread network name.
        
        Returns:
            Dictionary containing network name
        """
        return self._request("GET", "/node/network-name")

    def get_extended_panid(self) -> Dict[str, Any]:
        """Get the extended PAN ID of the network.
        
        Returns:
            Dictionary containing extended PAN ID
        """
        return self._request("GET", "/node/ext-panid")

    def get_partition_id(self) -> Dict[str, Any]:
        """Get the partition ID.
        
        Returns:
            Dictionary containing partition ID
        """
        return self._request("GET", "/node/partition-id")

    # Diagnostics
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get diagnostic information.
        
        Returns:
            Dictionary containing diagnostic data
        """
        return self._request("GET", "/diagnostics")

    def get_available(self) -> Dict[str, Any]:
        """Check if the OTBR service is available.
        
        Returns:
            Dictionary with availability status
        """
        return self._request("GET", "/available")

    # Network Data
    def get_network_data(self) -> Dict[str, Any]:
        """Get Thread network data.
        
        Returns:
            Dictionary containing network data
        """
        return self._request("GET", "/node/network-data")

    def get_active_dataset(self) -> Dict[str, Any]:
        """Get the active operational dataset.
        
        Returns:
            Dictionary containing active dataset
        """
        return self._request("GET", "/node/dataset/active")

    def set_active_dataset(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Set the active operational dataset.
        
        Args:
            dataset: Dictionary containing dataset parameters
            
        Returns:
            Response dictionary
        """
        return self._request("PUT", "/node/dataset/active", json=dataset)

    # Node Management
    def form_network(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Form a new Thread network.
        
        Args:
            config: Network configuration parameters
            
        Returns:
            Response dictionary
        """
        return self._request("POST", "/form", json=config)

    def join_network(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Join an existing Thread network.
        
        Args:
            config: Network configuration parameters
            
        Returns:
            Response dictionary
        """
        return self._request("POST", "/join", json=config)

    def leave_network(self) -> Dict[str, Any]:
        """Leave the current Thread network.
        
        Returns:
            Response dictionary
        """
        return self._request("POST", "/leave")

    # Properties
    def get_properties(self) -> Dict[str, Any]:
        """Get all OTBR properties.
        
        Returns:
            Dictionary containing all properties
        """
        return self._request("GET", "/properties")

    def get_property(self, property_name: str) -> Dict[str, Any]:
        """Get a specific property value.
        
        Args:
            property_name: Name of the property
            
        Returns:
            Dictionary containing property value
        """
        return self._request("GET", f"/properties/{property_name}")

    def set_property(self, property_name: str, value: Any) -> Dict[str, Any]:
        """Set a specific property value.
        
        Args:
            property_name: Name of the property
            value: New value for the property
            
        Returns:
            Response dictionary
        """
        return self._request("PUT", f"/properties/{property_name}", json={"value": value})


# Convenience function
def create_client(host: str = "localhost", port: int = 8081) -> OTBRClient:
    """Create an OTBR client instance.
    
    Args:
        host: The host address of the OTBR instance
        port: The port number (default: 8081)
        
    Returns:
        OTBRClient instance
    """
    return OTBRClient(host=host, port=port)


if __name__ == "__main__":
    # Example usage
    client = create_client()
    
    try:
        # Check availability
        print("Checking OTBR availability...")
        available = client.get_available()
        print(f"Available: {available}")
        
        # Get node information
        print("\nGetting node information...")
        node_info = client.get_node_info()
        print(f"Node Info: {node_info}")
        
    except requests.RequestException as e:
        print(f"Error connecting to OTBR: {e}")
