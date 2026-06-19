package io.github.aliasguard;

import org.keycloak.Config;
import org.keycloak.events.EventListenerProvider;
import org.keycloak.events.EventListenerProviderFactory;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.KeycloakSessionFactory;
import org.keycloak.provider.ServerInfoAwareProviderFactory;
import org.jboss.logging.Logger;

import java.util.Map;

public class AliasGuardEventListenerFactory implements EventListenerProviderFactory, ServerInfoAwareProviderFactory {

    public static final String ID = "alias-guard-listener";

    private static final Logger LOG = Logger.getLogger(AliasGuardEventListenerFactory.class);

    @Override
    public EventListenerProvider create(KeycloakSession session) {
        return new AliasGuardEventListener(session);
    }

    @Override
    public void init(Config.Scope config) {
    }

    @Override
    public void postInit(KeycloakSessionFactory factory) {
        LOG.infof(
                "Alias Guard loaded: component=event-listener provider-id=%s version=%s",
                ID,
                AliasGuardProviderInfo.version());
    }

    @Override
    public void close() {
    }

    @Override
    public String getId() {
        return ID;
    }

    @Override
    public Map<String, String> getOperationalInfo() {
        return AliasGuardProviderInfo.operationalInfo("event-listener", ID);
    }
}
