
We recommend that you refer [OSworld](#https://github.com/xlang-ai/OSWorld/tree/main) to configure the osworld environment.

## 💾 Installation
### On Your Desktop or Server (Non-Virtualized Platform)
1. First, clone this repository and `cd` into it. Then, install the dependencies listed in `requirements.txt`. It is recommended that you use the latest version of Conda to manage the environment, but you can also choose to manually install the dependencies. Please ensure that the version of Python is >= 3.9.
```bash
# Clone the OSWorld repository
git clone https://github.com/xlang-ai/OSWorld

# Change directory into the cloned repository
cd OSWorld

# Optional: Create a Conda environment for OSWorld
# conda create -n osworld python=3.9
# conda activate osworld

# Install required dependencies
pip install -e .
```
Alternatively, you can install the environment without any benchmark tasks:
```bash
pip install desktop-env
```
**We recommend that you install it with the local code.**


2. Install [VMware Workstation Pro](https://www.vmware.com/products/workstation-pro/workstation-pro-evaluation.html) (for systems with Apple Chips, you should install [VMware Fusion](https://www.vmware.com/go/getfusion)) and configure the `vmrun` command.  The installation process can refer to [How to install VMware Worksation Pro](./INSTALL_VMWARE.md). Verify the successful installation by running the following:
```bash
vmrun -T ws list
```
If the installation along with the environment variable set is successful, you will see the message showing the current running virtual machines.


## 🧪 Experiments
### Agent Baselines
If you wish to run the baseline agent, you can execute the following command as an example:

```bash
bash test.sh
```
You should modify the parameters in test.sh to match your path

