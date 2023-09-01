import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv

class MultiTaskGNN(nn.Module):
    def __init__(self, num_features, hidden_dim, num_classes, num_nodes):
        super(MultiTaskGNN, self).__init__()

        # Shared GCN layers
        self.gcn1 = GCNConv(num_features, hidden_dim)
        self.gcn2 = GCNConv(hidden_dim, hidden_dim)

        # Output layers for adjacency matrix prediction
        self.adj_fc1 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.adj_fc2 = nn.Linear(hidden_dim, num_nodes)

        # Output layers for edge label prediction
        self.edge_fc1 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.edge_fc2 = nn.Linear(hidden_dim, num_classes)

    def forward(self, x, edge_index):
        # Shared GCN layers
        x = F.relu(self.gcn1(x, edge_index))
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.gcn2(x, edge_index)

        # Compute pairwise node features for adjacency matrix and edge labels predictions
        x1 = x.unsqueeze(1).repeat(1, x.size(0), 1)
        x2 = x.unsqueeze(0).repeat(x.size(0), 1, 1)
        pairwise_features = torch.cat([x1, x2], dim=-1)

        # Adjacency matrix prediction branch
        adj_out = F.relu(self.adj_fc1(pairwise_features))
        adj_out = self.adj_fc2(adj_out)
        adj_out = adj_out.view(x.size(0), x.size(0))

        # Edge labels prediction branch
        edge_out = F.relu(self.edge_fc1(pairwise_features))
        edge_out = self.edge_fc2(edge_out)
        edge_out = edge_out.view(x.size(0), x.size(0), -1)

        return adj_out, edge_out