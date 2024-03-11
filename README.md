# Deploying HuggingFace TGI for Open Source LLMs in K8s / OpenShift with GitOps

The aim of this repository is to easily deploy our OpenSource LLMs in OpenShift or Kubernetes clusters using GitOps: 

![LLM0](/assets/llm0.png)

## Overview

[Text Generation Inference (TGI)](https://huggingface.co/docs/text-generation-inference/index) is a toolkit for deploying and serving Large Language Models (LLMs). TGI enables high-performance text generation for the most popular open-source LLMs, including Llama, Falcon, StarCoder, BLOOM, GPT-NeoX, and T5.

This repo will deploy [HuggingFace Text Generation Inference](https://github.com/huggingface/text-generation-inference) server deployments in K8s/OpenShift with GitOps:

![LLM2](/assets/llm1.png)

With this we can easily deploy different Open Source LLMs such as Llama2, Falcon, Mistral or FlanT5-XL among others in our OpenShift / Kubernetes clusters to be consumed as another application:

![LLM2](/assets/llm4.png)

## Requirements

- ROSA or OpenShift Clusters (can be also deployed in K8s with some tweaks)
- GPU available (24gb vRAM recommended)

### Configuring a GPU MachineSet in OpenShift

To deploy Large Language Models (LLMs) that require GPU resources, you need to ensure your OpenShift cluster has nodes with GPU capabilities. This section guides you through creating a GPU-enabled MachineSet in OpenShift.

**Prerequisites**

- Administrative access to an OpenShift cluster.
- The OpenShift Command Line Interface (CLI) `oc` installed and configured.

#### Steps

**Export Current MachineSet Configuration**
First, identify the name of an existing MachineSet you wish to clone for your GPU nodes. You can list all MachineSets in the `openshift-machine-api` namespace with:

```sh
oc get machinesets -n openshift-machine-api
```

Choose an existing MachineSet from the list and export its configuration:

```sh
oc get machineset <YOUR_MACHINESET_NAME> -n openshift-machine-api -o json > machine_set_gpu.json
```

**Modify the MachineSet Configuration for GPU**
Edit the `machine_set_gpu.json` file to configure the MachineSet for GPU nodes:

- Change the `metadata:name` to a new name that includes "GPU" to easily identify it (e.g., cluster-gpu-worker).
- Update the `spec:selector:matchLabels:machine.openshift.io/cluster-api-machineset` to match the new name.
- Adjust `spec:template:metadata:labels:machine.openshift.io/cluster-api-machineset` likewise.
*Additionally, modify the instance type and any other relevant specifications to suit your GPU requirements based on your cloud provider's offerings.*

Create the GPU MachineSet
Apply the updated MachineSet configuration to your cluster:

```sh
oc create -f machine_set_gpu.json
```

**Validate the GPU MachineSet Creation**
Confirm the new MachineSet is created and is provisioning nodes:

```sh
oc get machinesets -n openshift-machine-api | grep gpu
```

### Operators

##### Node Feature Discovery Operator

The Node Feature Discovery (NFD) Operator automatically detects and labels your OpenShift nodes with hardware features, like GPUs, making it easier to target workloads to specific hardware characteristics. Follow these steps to deploy NFD and verify its correct operation in your cluster, particularly for identifying nodes with NVIDIA GPUs.

##### Deploying the NFD Operator

1. **Access Installed Operators**:
   - Navigate to **Operators > Installed Operators** from the OpenShift web console's side menu.

2. **Install NFD**:
   - Locate the **Node Feature Discovery** entry in the list.
   - Click **NodeFeatureDiscovery** under the **Provided APIs** section.
   - Click **Create NodeFeatureDiscovery**.
   - On the setup screen, click **Create** to initiate the NFD Operator, which will start labeling nodes with detected hardware features.

##### Verifying NFD Operation

The NFD Operator uses vendor PCI IDs to recognize specific hardware. NVIDIA GPUs typically have the PCI ID `10de`.

**Using the OpenShift Web Console**:

1. Navigate to **Compute > Nodes** from the side menu.
2. Select a worker node known to have an NVIDIA GPU.
3. Click the **Details** tab.
4. Check under **Node Labels** for the label: `feature.node.kubernetes.io/pci-10de.present=true`. This label confirms the detection of an NVIDIA GPU.

**Using the CLI**:

To confirm the NFD has correctly labeled nodes with NVIDIA GPUs, run:

```sh
oc describe node | egrep 'Roles|pci' | grep -v master
```

You're looking for entries like feature.node.kubernetes.io/pci-10de.present=true among the node labels, indicating that the NFD Operator has successfully identified NVIDIA GPU hardware on your nodes.

*Note: The PCI vendor ID 0x10de is assigned to NVIDIA, serving as a unique identifier for their hardware components.*

#### NVIDIA GPU Operator

##### Installing the NVIDIA GPU Operator Using the Web Console

To install the NVIDIA GPU Operator in your OpenShift Container Platform, follow these steps:

1. From the OpenShift web console's side menu, navigate to **Operators > OperatorHub** and select **All Projects**.
2. In **Operators > OperatorHub**, search for the **NVIDIA GPU Operator**. For additional information, refer to the Red Hat OpenShift Container Platform documentation.
3. Select the **NVIDIA GPU Operator** and click **Install**. On the subsequent screen, click **Install** again.

##### Create the ClusterPolicy Instance

The installation of the NVIDIA GPU Operator introduces a custom resource definition for a ClusterPolicy, which configures the GPU stack, including image names and repository, pod restrictions/credentials, and more.

**Note**: Creating a ClusterPolicy with an empty specification, such as `spec: {}`, will cause the deployment to fail.

As a cluster administrator, you can create a ClusterPolicy using either the OpenShift Container Platform CLI or the web console. The steps differ when using NVIDIA vGPU; refer to the appropriate sections for details.

###### Create the Cluster Policy Using the Web Console

1. In the OpenShift Container Platform web console, from the side menu, select **Operators > Installed Operators** and click **NVIDIA GPU Operator**.
2. Select the **ClusterPolicy** tab, then click **Create ClusterPolicy**. The platform assigns the default name `gpu-cluster-policy`.

**Note**: While you can customize the ClusterPolicy, the defaults are generally sufficient for configuring and running the GPUs.

3. Click **Create**.

After creating the ClusterPolicy, the GPU Operator will install all necessary components to set up the NVIDIA GPUs in the OpenShift cluster. Allow at least 10-20 minutes for the installation process before initiating any troubleshooting, as it may take some time to complete.

The status of the newly deployed ClusterPolicy `gpu-cluster-policy` for the NVIDIA GPU Operator changes to `State: ready` upon successful installation.

##### Verify the Successful Installation of the NVIDIA GPU Operator

To confirm that the NVIDIA GPU Operator has been installed successfully, use the following command to view the new pods and daemonsets:

```sh
oc get pods,daemonset -n nvidia-gpu-operator
```

This command lists the pods and daemonsets deployed by the NVIDIA GPU Operator in the nvidia-gpu-operator namespace, indicating a successful installation.

### ArgoCD / OpenShift GitOps Operator

Deploying ArgoCD or the OpenShift GitOps Operator in your OpenShift cluster facilitates continuous deployment and management of applications and resources. Follow these steps to install and configure the OpenShift GitOps Operator, which includes ArgoCD as part of its deployment.

#### Installing the OpenShift GitOps Operator Using the Web Console

1. **Access OperatorHub**:
   - Navigate to **Operators > OperatorHub** from the OpenShift web console's side menu.
   - Ensure you're in the correct project or namespace where you wish to deploy the GitOps operator.

2. **Install the Operator**:
   - Search for the **OpenShift GitOps Operator** in the OperatorHub.
   - Select the Operator from the search results and click **Install**.
   - Follow the on-screen instructions, choosing the appropriate installation namespace (typically, this will be `openshift-gitops`) and approval strategy, then click **Install**.

#### Verifying the Operator Installation

After the installation, the OpenShift GitOps Operator will automatically deploy ArgoCD instances and other necessary components.

1. **Check the Installation Status**:
   - Navigate to **Installed Operators** under **Operators** in the side menu.
   - Ensure the **OpenShift GitOps Operator** status is showing as **Succeeded**.

2. **Access the ArgoCD Instance**:
   - From the OpenShift web console, go to **Applications > Routes** in the `openshift-gitops` namespace.
   - Look for a route named `openshift-gitops-server` and access the URL provided. This will take you to the ArgoCD dashboard.
   - Log in using your OpenShift credentials.

#### Configuring ArgoCD for Your Projects

Once ArgoCD is accessible, you can begin configuring it to manage deployments within your OpenShift cluster.

1. **Create Applications**: Define applications in ArgoCD, linking them to your Git repositories where your Kubernetes manifests, Helm charts, or Kustomize configurations are stored.

2. **Sync Policies**: Set up automatic or manual sync policies for your applications to align your cluster state with your Git repository's state.

3. **Monitor and Manage Deployments**: Use the ArgoCD dashboard to monitor deployments, manually trigger syncs, and rollback changes if necessary.

**Note**: The OpenShift GitOps Operator and ArgoCD leverage Kubernetes RBAC and OpenShift's SSO capabilities, allowing for detailed access control and auditing of your deployment workflows.

### Configuring Security Policies

For certain workloads or services in OpenShift, you may need to grant specific Security Context Constraints (SCCs) to service accounts to ensure they have the necessary permissions to run correctly. Below are commands to add various SCCs to the `default` service account in the `llms` namespace, which can be adjusted according to your specific requirements.

**Execute the following commands to apply the necessary SCCs:**

```sh
# Create the 'llms' namespace
oc create namespace llms

# Grant the 'anyuid' SCC to the 'default' service account
oc adm policy add-scc-to-user anyuid -z default --namespace llms

# Grant the 'nonroot' SCC to the 'default' service account
oc adm policy add-scc-to-user nonroot -z default --namespace llms

# Grant the 'hostmount-anyuid' SCC to the 'default' service account
oc adm policy add-scc-to-user hostmount-anyuid -z default --namespace llms

# Grant the 'machine-api-termination-handler' SCC to the 'default' service account
oc adm policy add-scc-to-user machine-api-termination-handler -z default --namespace llms

# Grant the 'hostnetwork' SCC to the 'default' service account
oc adm policy add-scc-to-user hostnetwork -z default --namespace llms

# Grant the 'hostaccess' SCC to the 'default' service account
oc adm policy add-scc-to-user hostaccess -z default --namespace llms

# Grant the 'node-exporter' SCC to the 'default' service account
oc adm policy add-scc-to-user node-exporter -z default --namespace llms

# Grant the 'privileged' SCC to the 'default' service account
oc adm policy add-scc-to-user privileged -z default --namespace llms
```

These commands facilitate the application's operation by ensuring that the default service account within your namespace has the permissions necessary to perform its operations. Modify the namespace and service account names as needed for your specific deployment scenario.

## Models available to deploy using GitOps

### [Mistral-7B-Instruct](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1)

```md
kubectl apply -k gitops/mistral
```

![LLM0](/assets/llm0.png)

### [Flan-T5-XXL](https://huggingface.co/google/flan-t5-xxl)

```md
kubectl apply -k gitops/flant5xxl
```

![LLM0](/assets/llm8.png)

### [Falcon-7B-Instruct](https://huggingface.co/tiiuae/falcon-7b-instruct)

```md
kubectl apply -k gitops/falcon
```

![LLM0](/assets/llm7.png)

### [Llama2-7B-Chat-HF](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)

```md
kubectl apply -k gitops/llama2
```

![LLM0](/assets/llm11.png)

![LLM0](/assets/llm12.png)

NOTE: this model needs to set the [HUGGING_FACE_HUB_TOKEN_BASE64](https://github.com/huggingface/text-generation-inference#using-a-private-or-gated-model) in a Secret to be downloaded.

```md
export HUGGING_FACE_HUB_TOKEN_BASE64=$(echo -n 'your-token-value' | base64)
envsubst < hg-tgi/overlays/llama2-7b/hf-token-secret-template.yaml > /tmp/hf-token-secret.yaml
kubectl apply -f /tmp/hf-token-secret.yaml -n llms
```

![LLM0](/assets/llm13.png)

### [CodeLlama-7b-Instruct-hf](https://huggingface.co/codellama/CodeLlama-7b-Instruct-hf)

```md
kubectl apply -k gitops/codellama
```

![LLM0](/assets/llm10.png)

### [StarCoder](https://huggingface.co/bigcode/starcoder)

```md
kubectl apply -k gitops/starcoder
```

NOTE: this model needs to set the [HF_TOKEN](https://github.com/huggingface/text-generation-inference#using-a-private-or-gated-model) in a Secret to be downloaded.

```md
export HUGGING_FACE_HUB_TOKEN_BASE64=$(echo -n 'your-token-value' | base64)
envsubst < hg-tgi/overlays/llama2-7b/hf-token-secret-template.yaml > /tmp/hf-token-secret.yaml
kubectl apply -f /tmp/hf-token-secret.yaml -n llms
```

![LLM0](/assets/llm9.png)

## Inference to the LLMs

* Check the [Inference Guide](./inference/README.md) to test your LLM deployed with Hugging Face Text Generation Inference 

## FrontEnd Gradio ChatBot powered by HF-TGI

We will deploy alongside the HF-TGI a Gradio ChatBot application with [Memory](https://python.langchain.com/docs/modules/memory/types/buffer) powered by [LangChain](https://python.langchain.com/docs/get_started/introduction).

This FrontEnd will be using the HF-TGI deployed as a backend, powering and fueling the AI NPL Chat capabilities of this FrontEnd Chatbot App.

![LLM0](/assets/llm3.png)

Once the Gradio ChatBot is deployed, will access directly to the HF-TGI Server that serves the LLM of your choice (see section below), and will answer your questions:

![LLM0](/assets/llm5.png)

NOTE: If you want to know more, check the [original source rh-aiservices-bu repository](https://github.com/rh-aiservices-bu/llm-on-openshift/blob/main/examples/ui/gradio/gradio-hftgi-memory/README.md). 

## Extra Notes

- Repo is heavily based in the [llm-on-openshift repo](https://github.com/rh-aiservices-bu/llm-on-openshift/tree/main/hf_tgis_deployment). Kudos to the team!
