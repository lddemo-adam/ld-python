// import * as LDClient from 'launchdarkly-js-client-sdk';

const element = document.getElementById('LD_listener');
my_client_id = "";

if(element) {
    try {
        my_client_id = element.dataset.clientid;
    } catch (error) {
        console.log("ERROR: client side id not set, flag change listener will likely fail");
    }
}
else {
    console.log("ERROR: could not get document element LD_listener, flag change listener will likely fail");
}

const client = LDClient.initialize(my_client_id, { key: 'user-key' });

client.on('ready', console.log("LD client ready for use."));

// TODO: flag name is hard coded here (twice)
client.on("update:demo-feature", function() {
    console.log("LD flag 'demo-feature' has been updated.");
    const newShowFeature = client.variation("demo-feature", false);
    console.log("New value for specific flag:", newShowFeature);
});

client.on("change:demo-feature", function() {
    console.log("LD flag 'demo-feature' has been updated.");
    const newShowFeature = client.variation("demo-feature", false);
    console.log("New value for specific flag:", newShowFeature);
}); 
