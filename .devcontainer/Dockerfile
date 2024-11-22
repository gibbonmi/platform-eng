FROM mcr.microsoft.com/vscode/devcontainers/base:bookworm as kind

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG KIND_RELEASE=v0.23.0

RUN export DEBIAN_FRONTEND=noninteractive

COPY docker.sh /tmp/scripts/
RUN chmod +x /tmp/scripts/docker.sh

# update the container
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install zsh ca-certificates gnupg -y && \
    apt-get autoremove -y && \
    apt-get clean -y

# INSTALL OF OTHER COMPONENTS

RUN /tmp/scripts/docker.sh

# change ownership of the home directory
RUN chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}

WORKDIR /home/${USERNAME}
USER ${USERNAME}

ENTRYPOINT [ "/usr/local/share/docker-init.sh" ]
CMD [ "sleep", "infinity" ]