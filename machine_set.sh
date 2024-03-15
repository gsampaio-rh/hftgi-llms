#!/bin/bash

# Automatically get the name of the first MachineSet
MACHINESET_NAME=$(oc get machinesets -n openshift-machine-api | awk 'NR==2{print $1}')

if [ -z "$MACHINESET_NAME" ]; then
    echo "Failed to find a MachineSet. Exiting."
    exit 1
fi

echo "Original MachineSet selected for cloning: $MACHINESET_NAME"

# Insert 'gpu' after '-worker-' in the MachineSet name
GPU_MACHINESET_NAME=$(echo "$MACHINESET_NAME" | sed 's/-worker-/-worker-gpu-/')

echo "New GPU MachineSet name will be: $GPU_MACHINESET_NAME"

# Step 1: Export the current MachineSet configuration
echo "Exporting current MachineSet configuration for ${MACHINESET_NAME}..."
oc get machineset "$MACHINESET_NAME" -n openshift-machine-api -o json > machine_set_gpu.json

if [ $? -ne 0 ]; then
    echo "Failed to export MachineSet configuration."
    exit 1
fi

# Modify the MachineSet JSON file for GPU, compatible with macOS's sed
sed -i '' "s/$MACHINESET_NAME/$GPU_MACHINESET_NAME/g" machine_set_gpu.json

# Assume modifications for GPU setup are made here
# This can include changing instance types, adding labels, or adjusting other configurations

# Step 3: Apply the modified MachineSet configuration
echo "Creating the GPU MachineSet..."
oc apply -f machine_set_gpu.json

if [ $? -ne 0 ]; then
    echo "Failed to create the GPU MachineSet."
    exit 1
fi

# Validation step: Check if the GPU MachineSet is correctly applied
echo "Validating the GPU MachineSet creation..."
oc get machineset -n openshift-machine-api | grep "$GPU_MACHINESET_NAME"

# End of script
