import os
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

from torchvision.models import swin_t
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR, ReduceLROnPlateau, CosineAnnealingLR

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

def fine_tune_swin_transformer(train_dataset_path: str,
                               val_dataset_path: str,
                               transform: transforms.Compose,
                               model_weight_path: str,
                               lr: float,
                               which_scheduler,
                               num_epoch: int,
                               batch_size: int,
                               device: torch.device,
                               path_to_save_fine_tuned_model: str,
                               desired_model_name: str,
                               **kwargs)-> None:
    """
    Fine-tunes a Swin Transformer model on a custom dataset.
    In this specific case, the model is fine-tuned on the cropped document dataset.
    Notice that concept is the same for other models and datasets.

    Args:
        - train_dataset_path (str): Path to the training dataset.
        - val_dataset_path (str): Path to the validation dataset.
        - test_dataset_path (str): Path to the test dataset.
        - transform (transforms.Compose): Transformations to be applied to the dataset.
        - model_weight_path (str): Path to the pre-trained model weights.
        - lr (float): Learning rate.
        - which_scheduler (str): Scheduler to be used during training.
        - num_epoch (int): Number of epochs.
        - batch_size (int): Batch size.
        - device (torch.device): Device to be used during training.
        - path_to_save_fine_tuned_model (str): Path to save the fine-tuned model.
        - desired_model_name (str): Name of the desired model to be fine-tuned.
        - **kwargs: Additional arguments such as parameters for the scheduler chosen.
            1- For StepLR: step_size and gamma.
            2- For ReduceLROnPlateau: factor and patience.
            3- For CosineAnnealingLR: TO DO (not implemented yet).

    Returns:
        - None
    """
    
    train_dataset = datasets.ImageFolder(root=train_dataset_path, transform=transform)
    val_dataset = datasets.ImageFolder(root=val_dataset_path, transform=transform)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    

    print(f"Classes: {train_dataset.classes}")
    print(f"Number of classes: {len(train_dataset.classes)}")

    model = swin_t()
    model.head = nn.Linear(model.head.in_features, len(train_dataset.classes))
    state_dict = torch.load(model_weight_path, weights_only=True)
    model.load_state_dict(state_dict)

    model_freezed = freeze_layers(model)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model_freezed.parameters(), lr=lr)

    if which_scheduler == 'StepLR':
        scheduler = StepLR(optimizer, step_size=kwargs.get("step_size"), gamma=kwargs.get("gamma"))
    elif which_scheduler == 'ReduceLROnPlateau':
        scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=kwargs.get("factor"), patience=kwargs.get("patience"))
    elif which_scheduler == 'CosineAnnealingLR':
        pass
    else:
        raise ValueError("The scheduler is not supported. Verify the name of the scheduler passed as argument. Or call import it from torch.optim.lr_scheduler.") 
    model_freezed.to(device)
    
    train_losses = []
    val_losses = []
    train_accs = []
    val_accs = []

    for epoch in range(num_epoch):
        print(f"Epoch {epoch+1}/{num_epoch}")
        train_loss, train_acc = train_step(model_freezed, criterion, optimizer, train_loader, device)
        val_loss, val_acc = val_step(model_freezed, criterion, val_loader, device)
        if isinstance(scheduler, ReduceLROnPlateau):
            scheduler.step(val_loss)
        else:
            scheduler.step()
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_accs.append(train_acc)
        val_accs.append(val_acc)
    saving_path = os.path.join(path_to_save_fine_tuned_model, f"{desired_model_name}_fine_tuned.pth")
    torch.save(model_freezed.state_dict(), saving_path)
    print(f"Model saved at {saving_path}")

def freeze_layers(model: torch.nn.Module):
    """
    Freezes the layers of a model.
    In this specific case, the layers head and avgpool are defined as trainable.
    """
    for param in model.parameters():
        param.requires_grad = False

    for param in model.head.parameters():
        param.requires_grad = True
    
    for param in model.avgpool.parameters():
        param.requires_grad = True

    return model

def train_step(model: torch.nn.Module, 
               criterion: torch.nn.Module, 
               optimizer: torch.optim.Optimizer, 
               train_loader: DataLoader, 
               device: torch.device):
    """
    Trains a model for one epoch.
    """

    model.train()
    running_loss = 0.0
    running_corrects = 0
    total = 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        
        outputs = model(images)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, preds = torch.max(outputs, 1)
        total += labels.size(0)
        running_corrects += (preds == labels).sum().item()

    train_loss = running_loss / len(train_loader)
    train_acc = 100*running_corrects / total
    print(f"Train Loss: {train_loss:.4f} || Train Acc: {train_acc:.2f}")

    return train_loss, train_acc

def val_step(model: torch.nn.Module,
            criterion: torch.nn.Module,
            val_loader: DataLoader,
            device: torch.device):
        """
        Validates a model for one epoch
        """

        model.eval()
        running_loss = 0.0
        running_corrects = 0
        total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)

                outputs = model(images)
                loss = criterion(outputs, labels)

                running_loss += loss.item()
                _, preds = torch.max(outputs, 1)
                total += labels.size(0)
                running_corrects += (preds == labels).sum().item()
        
        val_loss = running_loss / len(val_loader)
        val_acc = 100*running_corrects / total
        print(f"Val Loss: {val_loss:.4f} || Val Acc: {val_acc:.2f}")

        return val_loss, val_acc

def plot_metrics(total_epoch: int,
                 train_losses: list,
                 val_losses: list, 
                 train_accs: list, 
                 val_accs: list,
                 path_to_save_plot: str)-> None:
    """
    Plots the training and validation losses and accuracies.

    Args:
        - total_epoch (int): Number of epochs
        - train_losses (list): Training losses.
        - val_losses (list): Validation losses.
        - train_accs (list): Training accuracies.
        - val_accs (list): Validation accuracies.
        - path_to_save_plot (str): Path to save the plot.
        
    Returns:
        - None. However, it will save the plot in specific path.
    """

    saving_path = os.path.join(path_to_save_plot, "Training_metrics.png")
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.plot(range(1, total_epoch+1), train_losses, label='Train Loss')
    plt.plot(range(1, total_epoch+1), val_losses, label='Val Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.title('Training and Validation Losses')
    plt.legend()
    plt.grid(axis='both')

    plt.subplot(1, 2, 2)
    plt.plot(range(1, total_epoch+1), train_accs, label='Train Accuracy')
    plt.plot(range(1, total_epoch+1), val_accs, label='Val Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy (%)')
    plt.title('Training and Validation Accuracies')
    plt.legend()
    plt.grid(axis='both')

    plt.tight_layout()
    plt.savefig(saving_path)

def test_model(model: torch.nn.Module,
               test_dataset_path: str,
               transform: transforms.Compose,
               batch_size: int,
               fine_tuned_model_path: str,
               device: torch.device):
    """
    Tests a model on a test dataset.
    """
    test_dataset = datasets.ImageFolder(root=test_dataset_path, transform=transform)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    criterion = nn.CrossEntropyLoss()
    

    model = swin_t()
    model.head = nn.Linear(model.head.in_features, len(test_dataset.classes))
    state_dict = torch.load(fine_tuned_model_path, weights_only=True)
    model.load_state_dict(state_dict)
    model.to(device)

    model.eval()
    running_loss = 0.0
    running_corrects = 0
    total = 0

    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)
            running_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            total += labels.size(0)
            running_corrects += (preds == labels).sum().item()

    test_loss = running_loss / len(test_loader)
    test_acc = 100*running_corrects / total
    print(f"Test Loss: {test_loss:.4f} || Test Acc: {test_acc:.2f}")

