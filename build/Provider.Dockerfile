FROM scratch
COPY *.jar /jar/
LABEL org.opencontainers.image.title="keycloak-alias-guard"
LABEL org.opencontainers.image.description="Keycloak SPI: canonical email validation to prevent mailbox alias abuse"
LABEL org.opencontainers.image.source="https://github.com/dnwsilver/keycloak-alias-guard"
