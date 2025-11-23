import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from federated_learning.server import start_server
from federated_learning.client import HealthRiskClient
from federated_learning.data_loader import FederatedHealthDataset
from data_simulation.wearables import WearableSimulator
from data_simulation.air_quality import EnvironmentalSimulator
import flwr as fl

def create_client(cid: str):
    wear_sim = WearableSimulator(num_patients=500)  # Increase from 50
    env_sim = EnvironmentalSimulator(num_sensors=20)  # Increase from 5
    
    health_data = wear_sim.generate_daily_data("2024-01-15", node_id=f"hospital_{cid}")
    env_data = env_sim.generate_sensor_data(node_id=f"hospital_{cid}")
    
    print(f"📦 Client {cid} health_data: {len(health_data)} rows")
    print(f"📦 Client {cid} env_data: {len(env_data)} rows")
    
    train_dataset = FederatedHealthDataset(health_data, env_data)
    val_dataset = FederatedHealthDataset(health_data, env_data)
    
    train_loader = train_dataset.get_dataloader(batch_size=32)
    val_loader = val_dataset.get_dataloader(batch_size=32)
    
    return HealthRiskClient(cid, train_loader, val_loader)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_federated.py [server|client <client_id>]")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "server":
        start_server(num_rounds=10, min_clients=2, port=5050)  # Fewer rounds for testing
    elif mode == "client":
        cid = sys.argv[2]
        server_address = os.getenv("SERVER_ADDRESS", "127.0.0.1:5050")
        print(f"🚀 Starting client {cid}...")
        print(f"🔗 Connecting to server at {server_address}")
        fl.client.start_client(
            server_address=server_address,
            client=create_client(cid)
        )