package io.github.aliasguard;

import org.keycloak.events.Event;
import org.keycloak.events.EventListenerProvider;
import org.keycloak.events.EventType;
import org.keycloak.events.admin.AdminEvent;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.RealmModel;
import org.keycloak.models.UserModel;

public class AliasGuardEventListener implements EventListenerProvider {

    private final KeycloakSession session;

    public AliasGuardEventListener(KeycloakSession session) {
        this.session = session;
    }

    @Override
    public void onEvent(Event event) {
        if (!isRelevant(event.getType()) || event.getUserId() == null || event.getRealmId() == null) {
            return;
        }

        RealmModel realm = session.realms().getRealm(event.getRealmId());
        UserModel user = session.users().getUserById(realm, event.getUserId());
        if (user == null) {
            return;
        }

        String email = user.getEmail();
        if (email == null || email.isBlank()) {
            return;
        }

        user.setSingleAttribute(EmailCanonicalizer.ATTRIBUTE_NAME, EmailCanonicalizer.canonicalize(email));
    }

    @Override
    public void onEvent(AdminEvent event, boolean includeRepresentation) {
    }

    @Override
    public void close() {
    }

    private static boolean isRelevant(EventType type) {
        return type == EventType.REGISTER
                || type == EventType.UPDATE_EMAIL
                || type == EventType.UPDATE_PROFILE;
    }
}
