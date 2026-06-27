import { createClient } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';

window.cortexGenLayer = {
  async read(address, functionName, args = []) {
    const client = createClient({ chain: testnetBradbury });
    return client.readContract({ address, functionName, args });
  },

  async write(address, account, functionName, args = []) {
    const client = createClient({ chain: testnetBradbury, account });
    return client.writeContract({
      address,
      functionName,
      args,
      value: 0n,
    });
  },
};

