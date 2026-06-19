package io.github.aliasguard;

import java.util.Objects;
import java.util.stream.Stream;

import org.keycloak.models.KeycloakSession;
import org.keycloak.models.RealmModel;
import org.keycloak.models.UserModel;

final class MailboxDuplicateChecker {

    private MailboxDuplicateChecker() {
    }

    static boolean exists(KeycloakSession session, RealmModel realm, String email, UserModel excludeUser) {
        String canonical = EmailCanonicalizer.canonicalize(email);
        if (canonical == null || canonical.isBlank()) {
            return false;
        }

        String excludeId = excludeUser != null ? excludeUser.getId() : null;

        if (hasUserWithCanonicalAttribute(session, realm, canonical, excludeId)) {
            return true;
        }

        if (hasUserWithEmail(session, realm, canonical, excludeId)) {
            return true;
        }

        return hasLegacyUserWithCanonicalEmail(session, realm, canonical, excludeId);
    }

    private static boolean hasUserWithCanonicalAttribute(
            KeycloakSession session,
            RealmModel realm,
            String canonical,
            String excludeId) {
        try (Stream<UserModel> users =
                session.users().searchForUserByUserAttributeStream(realm, EmailCanonicalizer.ATTRIBUTE_NAME, canonical)) {
            return users.anyMatch(user -> !Objects.equals(user.getId(), excludeId));
        }
    }

    private static boolean hasUserWithEmail(
            KeycloakSession session, RealmModel realm, String email, String excludeId) {
        UserModel user = session.users().getUserByEmail(realm, email);
        if (user == null || Objects.equals(user.getId(), excludeId)) {
            return false;
        }

        return canonicalMatches(email, user.getEmail());
    }

    private static boolean hasLegacyUserWithCanonicalEmail(
            KeycloakSession session, RealmModel realm, String canonical, String excludeId) {
        int at = canonical.indexOf('@');
        if (at <= 0) {
            return false;
        }

        String localPart = canonical.substring(0, at);
        try (Stream<UserModel> candidates = session.users().searchForUserStream(realm, localPart, 0, 50)) {
            return candidates
                    .filter(user -> !Objects.equals(user.getId(), excludeId))
                    .map(UserModel::getEmail)
                    .filter(Objects::nonNull)
                    .anyMatch(existingEmail -> canonicalMatches(canonical, existingEmail));
        }
    }

    private static boolean canonicalMatches(String canonical, String email) {
        return canonical.equals(EmailCanonicalizer.canonicalize(email));
    }
}
