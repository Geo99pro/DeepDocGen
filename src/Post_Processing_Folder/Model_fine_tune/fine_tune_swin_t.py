import os
import torch
import torch.nn as nn
import torchvision
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import swin_t
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torchinfo import summary

os.environ['CUDA_VISIBLE_DEVICES'] = "0"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

train_transforms = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=15), 
    transforms.RandomResizedCrop(size=224, scale=(0.8, 1.0)),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1), 
    transforms.ToTensor(), 
    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
])

val_transforms = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
])


class EarlyStopper:
    """
    This class is used to implement the early stopping mechanism. From: https://stackoverflow.com/questions/71998978/early-stopping-in-pytorch
    """
    def __init__(self, patience=1, min_delta=0):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.min_validation_loss = float('inf')

    def early_stop(self, validation_loss):
        if validation_loss < self.min_validation_loss - self.min_delta:
            self.min_validation_loss = validation_loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                return True
        return False


def get_data(train_data, val_data, train_transforms, val_transforms,  batch_size, should_shuffle)->tuple[datasets.ImageFolder, datasets.ImageFolder, int]:
    """
    This function is used to get the data loaders.

    Args:
        - train_data (str): The path to the training data.
        - val_data (str): The path to the validation data.
        - train_transforms (torchvision.transforms.Compose): The transformations for the training data.
        - val_transforms (torchvision.transforms.Compose): The transformations for the validation data.
        - batch_size (int): The batch size.
        - should_shuffle (bool): Whether to shuffle the data or not.

    Returns:
        - train_loader (torch.utils.data.DataLoader): The data loader for the training data.
        - val_loader (torch.utils.data.DataLoader): The data loader for the validation data.
        - len(train_dataset.classes) (int): The number of classes in the dataset.
    """
    
    train_dataset = datasets.ImageFolder(root=train_data, transform=train_transforms)
    val_dataset = datasets.ImageFolder(root=val_data, transform=val_transforms)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=should_shuffle)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=should_shuffle)

    if train_dataset.classes != val_dataset.classes:
        raise ValueError('The classes in the datasets are inconsistent. Please check the data.')

    print(f"The dataset has {len(train_dataset.classes)} classes: {train_dataset.classes}")
    return train_loader, val_loader, len(train_dataset.classes)

def prepare_model(model_name, num_classes, is_weight_available_locally, train_only_last_layer, device, **kwargs)->torch.nn.Module:
    """
    This function is used to prepare the model.

    Args:
        - model_name (str): The name of the model.
        - num_classes (int): The number of classes in the dataset.
        - is_weight_available_locally (bool): Whether the weights are available locally or not.
        - train_only_last_layer (bool): Whether to train only the last layer or not.
        - device (torch.device): The device to use.
        - **kwargs: Additional arguments. Like the weight path.

    Returns:
        - model (torch.nn.Module): The model.
    """
    if model_name == 'swin_t':
        if is_weight_available_locally:
            model = swin_t()
            state_dict = torch.load(kwargs.get('weight_path'), weights_only=True)
            model.load_state_dict(state_dict)
            model.head = nn.Linear(model.head.in_features, num_classes)
        else:
            model = swin_t(weights=kwargs.get('weights', 'IMAGENET1K_V1'))
            model.head = nn.Linear(model.head.in_features, num_classes)
    else:
        raise ValueError('Only swin_t is supported for now.')

    if train_only_last_layer:
        for param in model.parameters():
            param.requires_grad = False
        for param in model.head.parameters():
            param.requires_grad = True
    return model.to(device)

def plot_curve(total_epoch, train_loss, val_loss, train_accuracies, val_accuracies, fig_path):
    """
    This function is used to plot the training and validation curves.

    Args:
        - total_epoch (int): The total number of epochs.
        - train_loss (list): The training loss.
        - val_loss (list): The validation loss.
        - train_accuracies (list): The training accuracies.
        - val_accuracies (list): The validation accuracies.
        - fig_path (str): The path to save the figure.

    Returns:
        - None. However, it saves the figure in the specified path.
    """

    plt.figure(figsize=(10, 4))

    plt.subplot(1, 2, 1)
    plt.plot(range(1, total_epoch + 1), train_loss, label='Train Loss')
    plt.plot(range(1, total_epoch + 1), val_loss, label='Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.title('Train and Validation Loss')
    plt.legend()
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(range(1, total_epoch + 1), train_accuracies, label='Train Accuracy')
    plt.plot(range(1, total_epoch + 1), val_accuracies, label='Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy (%)')
    plt.title('Train and Validation Accuracy')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    os.makedirs(fig_path, exist_ok=True)
    plt.savefig(os.path.join(fig_path, 'train_val_curves.png'))
    plt.close()

def run_process(total_epoch, 
                train_data_path, 
                val_data_path, 
                batch_size, 
                lr, 
                patience, 
                min_delta, 
                path_to_save_fine_tuned_model, 
                path_to_save_plot_curve, 
                local_weight_path=None)->tuple[list]:
    """
    This function is used to run the fine-tuning process.
    
    Args:
        - total_epoch (int): The total number of epochs.
        - train_data_path (str): The path to the training data.
        - val_data_path (str): The path to the validation data.
        - batch_size (int): The batch size.
        - lr (float): The learning rate.
        - patience (int): The patience for early stopping.
        - min_delta (float): The minimum delta for early stopping.
        - path_to_save_fine_tuned_model (str): The path to save the fine-tuned model.
        - path_to_save_plot_curve (str): The path to save the plot curve.
        - local_weight_path (str): The path to the local weight.

    Returns:
        - train_loss (list): The training loss.
        - val_loss (list): The validation loss.
        - train_accuracies (list): The training accuracies.
        - val_accuracies (list): The validation accuracies.
    """
    train_loader, val_loader, num_classes = get_data(train_data_path, 
                                                val_data_path, 
                                                train_transforms, 
                                                val_transforms, 
                                                batch_size, 
                                                should_shuffle=True)

    model = prepare_model(model_name='swin_t',
                        num_classes=num_classes,
                        is_weight_available_locally=(local_weight_path is not None),
                        train_only_last_layer=True,
                        device=device,
                        weight_path=local_weight_path)

    model_sumarry = summary(model,
                            input_size = (batch_size, 3, 224, 224),
                            col_names = ["input_size", "output_size", "num_params", "trainable"], col_width = 30,
                            row_settings=["var_names"])
    print(model_sumarry)

    criterion = nn.CrossEntropyLoss()
    #optimizer = torch.optim.Adam(model.parameters(), lr=lr) # Adam optimizer
    optimizer = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=1e-4)
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=3)
    early_stopper = EarlyStopper(patience=patience, min_delta=min_delta)

    train_loss, val_loss = [], []
    train_accuracies, val_accuracies = [], []

    for epoch in range(1, total_epoch + 1):

        model.train()
        correct, total, running_loss = 0, 0, 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        train_loss_epoch = running_loss / len(train_loader)
        train_accuracy_epoch = 100 * correct / total

        model.eval()
        correct, total, running_loss = 0, 0, 0.0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)

                outputs = model(images)
                loss = criterion(outputs, labels)

                running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        val_loss_epoch = running_loss / len(val_loader)
        val_accuracy_epoch = 100 * correct / total

        train_loss.append(train_loss_epoch)
        train_accuracies.append(train_accuracy_epoch)
        val_loss.append(val_loss_epoch)
        val_accuracies.append(val_accuracy_epoch)
        scheduler.step(val_loss_epoch)

        if early_stopper.early_stop(val_loss_epoch):
            print(f"Early stop at the {epoch}. Validation loss: {val_loss_epoch:.4f}")
            break

        print(f"Epoch {epoch}/{total_epoch} - training loss: {train_loss_epoch:.4f}, "
            f"Training Accuracy: {train_accuracy_epoch:.2f}%, "
            f"Val loss: {val_loss_epoch:.4f}, "
            f"Validation Accuracy: {val_accuracy_epoch:.2f}%")

    os.makedirs(path_to_save_fine_tuned_model, exist_ok=True)
    torch.save(model.state_dict(), os.path.join(path_to_save_fine_tuned_model, 'swin_t_fine_tuned_docly_publy_50_ep.pth'))
    plot_curve(total_epoch, train_loss, val_loss, train_accuracies, val_accuracies, fig_path=path_to_save_plot_curve)

    return train_loss, val_loss, train_accuracies, val_accuracies