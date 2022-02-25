# Block ordering (sequential block) 
bs = blocks = df['Blockno']
first_block = bs.iloc[0]
last_block =  14277181 # bs.iloc[-1]
no_blocks = last_block - first_block
divs = list(divisors(no_blocks))
print(divs)
mod = int(input("Select divisor: "))
n_iter = no_blocks // mod
print("n_iter:", n_iter)

xs = []
for i in range(n_iter):
    if i % 10 == 1:
        print("iter {} of {}".format(i, n_iter))
    sb = first_block + (mod * i)
    eb = first_block + mod * (i+1)
    x = get_tx_window(sb, eb)
    xs.append(x)
print("Done!")
n_txs = sum(lengths(xs))
print("Total txs:", n_txs)

d = reduce_df(list(map(lambda x: pd.DataFrame(x), xs)))
values = d.iloc[logical2idx(d['value'].astype(float) > 0.0)]

# Hash ordering (dict map)
hs = hashes = df['Txhash']


# Timestamp ordering (unix)
ts = timestamps = df['UnixTimestamp']


def ordered_range(lo, hi, groups):
    return groupl(range(lo, hi), groups)

def ordered_group(length, groups):
    return groupl(range(length), groups)


# GET BLOCK TXS 
# https://ethereum.stackexchange.com/questions/102459/list-all-transactions-for-a-block
cmd = 'geth --syncmode "light"'
import web3
w3 = web3.Web3(web3.Web3.IPCProvider('/home/user/.ethereum/geth.ipc'))
block = w3.eth.get_block(12704257) # example for a recent block
for tx_hash in block['transactions']:
    tx = w3.eth.get_transaction(tx_hash)
    tx_obj = {'addr_sender': tx['from'], 'addr_receiver': tx['to'], 'value': tx['value']}