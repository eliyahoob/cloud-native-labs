# Ubuntu OS	   
FROM ubuntu:22.04

# Tell Ubuntu: Do not show interactive menus.											 
ENV DEBIAN_FRONTEND=noninteractive

# Commands: update system, install: Ansible, SSH tools, GIT.															
RUN apt-get update && apt-get install -y \
    ansible \
    openssh-client \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establish runtime SSH key layouts (Create the .ssh directory inside the master container for root user)
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh
# Copy the private key (the key itself) into the Master's SSH directory																	   
COPY ansible-key /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

# Disable SSH strict host key checking (prevents manual "yes/no" prompts)
RUN echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

# Set the default working directory where playbooks will sit															
WORKDIR /ansible
CMD ["tail", "-f", "/dev/null"]