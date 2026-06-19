package io.github.aliasguard;

import java.util.Locale;
import java.util.Set;

public final class EmailCanonicalizer {

    public static final String ATTRIBUTE_NAME = "email_canonical";

    private static final Set<String> GMAIL_DOMAINS = Set.of("gmail.com", "googlemail.com");

    private EmailCanonicalizer() {
    }

    public static String canonicalize(String email) {
        if (email == null) {
            return null;
        }

        String trimmed = email.trim().toLowerCase(Locale.ROOT);
        int at = trimmed.lastIndexOf('@');
        if (at < 1 || at == trimmed.length() - 1) {
            return trimmed;
        }

        String local = trimmed.substring(0, at);
        String domain = trimmed.substring(at + 1);

        if (GMAIL_DOMAINS.contains(domain)) {
            local = stripPlus(local).replace(".", "");
            domain = "gmail.com";
        } else {
            local = stripPlus(local);
        }

        return local + "@" + domain;
    }

    private static String stripPlus(String local) {
        int plus = local.indexOf('+');
        return plus >= 0 ? local.substring(0, plus) : local;
    }
}
