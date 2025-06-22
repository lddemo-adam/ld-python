    import * as LDClient from 'launchdarkly-js-client-sdk';

    const client = LDClient.initialize('sdk-fad800e4-2188-45ce-aac0-27a022667260', { key: 'user-key' });

    client.on("update:demo-feature", function() {
        console.log("LD flag 'demo-feature' has been updated.");
        const newShowFeature = client.variation("your-feature-flag-key", false);
        console.log("New value for specific flag:", newShowFeature);
    });