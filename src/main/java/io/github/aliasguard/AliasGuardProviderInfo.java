package io.github.aliasguard;

import java.util.LinkedHashMap;
import java.util.Map;

final class AliasGuardProviderInfo {

    static final String ARTIFACT_ID = "keycloak-alias-guard";

    private AliasGuardProviderInfo() {
    }

    static String version() {
        Package pkg = AliasGuardProviderInfo.class.getPackage();
        if (pkg != null && pkg.getImplementationVersion() != null) {
            return pkg.getImplementationVersion();
        }
        return "unknown";
    }

    static Map<String, String> operationalInfo(String component, String providerId) {
        Map<String, String> info = new LinkedHashMap<>();
        info.put("artifact", ARTIFACT_ID);
        info.put("component", component);
        info.put("provider-id", providerId);
        info.put("version", version());
        return info;
    }
}
