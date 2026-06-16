#OS: Ubuntu
FROM ubuntu:22.04
						  
# Update system and install SSH
RUN apt-get update && apt-get install -y \
    openssh-server \			 
    curl \
    && mkdir /var/run/sshd

# Set SSH key for root user
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh

# Copy the public key into the "authorized_keys" file
COPY ansible-key.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

# Configure SSH daemon to permit root login and public key auth
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# Install Docker (in the Ansible-Slave Docker container)
RUN curl -fsSL https://get.docker.com | sh

# Open SSH port
EXPOSE 22

# Run SSH service in the backround
CMD ["/usr/sbin/sshd", "-D"]