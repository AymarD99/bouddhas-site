const CONFIG = {
  storeDomain: 'my-bouddha-store.myshopify.com',
  storefrontToken: 'a86df8c1a0e19136d077077520e22e07',
  apiVersion: '2024-07',
  get apiUrl() {
    return `https://${this.storeDomain}/api/${this.apiVersion}/graphql.json`
  }
};
