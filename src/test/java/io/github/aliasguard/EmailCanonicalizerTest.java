package io.github.aliasguard;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class EmailCanonicalizerTest {

    @Test
    void canonicalizesGmailPlusTagAndDots() {
        assertEquals("user@gmail.com", EmailCanonicalizer.canonicalize("U.Ser+promo@GoogleMail.com"));
    }

    @Test
    void canonicalizesGooglemailDomain() {
        assertEquals("user@gmail.com", EmailCanonicalizer.canonicalize("user@googlemail.com"));
    }

    @Test
    void stripsPlusForNonGmailDomains() {
        assertEquals("john@outlook.com", EmailCanonicalizer.canonicalize("john+2@outlook.com"));
    }

    @Test
    void keepsDotsForNonGmailDomains() {
        assertEquals("john.smith@yahoo.com", EmailCanonicalizer.canonicalize("john.smith@yahoo.com"));
    }

    @Test
    void lowercasesEmail() {
        assertEquals("user@example.com", EmailCanonicalizer.canonicalize("User@Example.com"));
    }

    @Test
    void trimsWhitespace() {
        assertEquals("user@gmail.com", EmailCanonicalizer.canonicalize("  user@gmail.com  "));
    }
}
