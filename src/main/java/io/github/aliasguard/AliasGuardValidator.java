package io.github.aliasguard;

import org.keycloak.Config;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.KeycloakSessionFactory;
import org.keycloak.models.RealmModel;
import org.keycloak.models.UserModel;
import org.keycloak.provider.ServerInfoAwareProviderFactory;
import org.keycloak.userprofile.UserProfileAttributeValidationContext;
import org.keycloak.validate.AbstractStringValidator;
import org.keycloak.validate.ValidationContext;
import org.keycloak.validate.ValidationError;
import org.keycloak.validate.Validator;
import org.keycloak.validate.ValidatorConfig;
import org.jboss.logging.Logger;

import java.util.Map;

public class AliasGuardValidator extends AbstractStringValidator implements ServerInfoAwareProviderFactory {

    public static final String ID = "alias-guard";
    public static final String ERROR_MAILBOX_NOT_UNIQUE = "error-mailbox-not-unique";

    private static final Logger LOG = Logger.getLogger(AliasGuardValidator.class);
    private static final AliasGuardValidator INSTANCE = new AliasGuardValidator();

    @Override
    public String getId() {
        return ID;
    }

    @Override
    public Validator create(KeycloakSession session) {
        return INSTANCE;
    }

    @Override
    public void init(Config.Scope config) {
    }

    @Override
    public void postInit(KeycloakSessionFactory factory) {
        LOG.infof(
                "Alias Guard loaded: component=validator provider-id=%s version=%s",
                ID,
                AliasGuardProviderInfo.version());
    }

    @Override
    public void close() {
    }

    @Override
    public Map<String, String> getOperationalInfo() {
        return AliasGuardProviderInfo.operationalInfo("validator", ID);
    }

    @Override
    protected void doValidate(String value, String inputHint, ValidationContext context, ValidatorConfig config) {
        UserProfileAttributeValidationContext profileContext = UserProfileAttributeValidationContext.from(context);
        UserModel user = profileContext.getAttributeContext().getUser();
        RealmModel realm = context.getSession().getContext().getRealm();

        if (MailboxDuplicateChecker.exists(context.getSession(), realm, value, user)) {
            context.addError(new ValidationError(ID, inputHint, ERROR_MAILBOX_NOT_UNIQUE, value));
        }
    }
}
