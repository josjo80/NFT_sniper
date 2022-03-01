import json
import xlsxwriter

from statistics import median
from statistics import median_grouped
from statistics import geometric_mean
from statistics import harmonic_mean


class Category:
    '''Contain info on category including counts and stuff'''
    def __init__(self, name):
        self.name = name
        self.traits = []
        self.trait_count = {}
        self.trait_freq = {}
        self.trait_rarity = {}
        self.trait_rarity_normed = {}


class Collection:
    '''Representation of an entire collection of items'''
    def __init__(self):
        self.traits = []                # List of tuples coupling (category, trait)
        self.item_count = 0             # Number of items in collection
        self.items = []                 # List of all item objects in collection
        self.trait_count = {}           # Mapping of number of traits to count
        self.categories = {}            # Dict of all categories in collection with counts and stuff

    def get_avg_trait_per_cat(self):
        '''Return the average number of traits per category'''
        traits_per_cat = []
        for c in self.categories.values():
            traits_per_cat.append(len(c.traits))
        return sum(traits_per_cat)/len(traits_per_cat)

    def get_med_trait_per_cat(self):
        traits_per_cat = []
        for c in self.categories.values():
            traits_per_cat.append(len(c.traits))
        return median(traits_per_cat)

    def get_gm_trait_per_cat(self):
        traits_per_cat = []
        for c in self.categories.values():
            traits_per_cat.append(len(c.traits))
        return geometric_mean(traits_per_cat)

    def get_hm_trait_per_cat(self):
        traits_per_cat = []
        for c in self.categories.values():
            traits_per_cat.append(len(c.traits))
        return harmonic_mean(traits_per_cat)

    def get_avg_med_gm_hm(self):
        return (self.get_avg_trait_per_cat()*self.get_med_trait_per_cat()* \
            self.get_gm_trait_per_cat()*self.get_hm_trait_per_cat())**0.25

    def get_avg_gm_hm(self):
        return (self.get_avg_trait_per_cat()*self.get_gm_trait_per_cat())**(1/2)


class Item:
    '''Representation of item in a collection'''
    def __init__(self, data):
        '''Take data in from json file to create items'''
        self.traits = {}
        self.traits["trait_count"] = 0
        self.stat_rarity = 1
        self.rarity_score = 0
        self.rarity_score_normed = 0
        for a in data['attributes']:
            if a["trait_type"] == "Generation":
                self.ID = a["value"]             
            elif a["trait_type"] == "birthday":
                self.birthday = a["value"]
            else:
                self.traits[a["trait_type"]] = a["value"]
                self.traits["trait_count"] += 1


# Loop over the json file and add items to collection and count them
input_file = '../data/pudgypenguins_data_raw'
x = json.load(open(input_file, 'r'))
data = x['pudgypenguins']
md = data['project_metadata']
nfts = data['nfts']

collection = Collection()

for (nm, nft) in nfts.items():
    nft['attributes'].append({'trait_type': 'Generation', 'value': nm})
    collection.items.append(Item(nft))
    collection.item_count += 1

# Loop over items in collection to get list of all category/trait tuples
for i in collection.items:
    for c, t in i.traits.items():
        if (c, t) not in collection.traits:
            collection.traits.append((c, t))
        else:
            pass

# Loop over items in collection to add None type to items and sort and create category objects
for i in collection.items:
    for t in collection.traits:
        # If item has empty attributes/traits in categories make them explicity None
        if t[0] not in i.traits.keys():
            i.traits[t[0]] = None
        # Set up category objects in collection
        if t[1] not in collection.categories.keys():
            collection.categories[t[0]] = Category(t[0])
    #i.traits = dict( sorted(i.traits.items(), key=lambda x: x[0].lower()) )
    #collection.categories = dict( sorted(collection.categories.items(), key=lambda x: x[0].lower()) )

# Loop over items in collection and count trait occurrences into category objects
for i in collection.items:
    for c, t in i.traits.items():
        #print(i.ID, t, v)
        if t in collection.categories[c].traits:
            collection.categories[c].trait_count[t] += 1
        else:
            collection.categories[c].traits.append(t)
            collection.categories[c].trait_count[t] = 1

# Loop over categories and calculate frequency and rarity score
for c in collection.categories.values():
    for t in c.traits:
        c.trait_freq[t] = c.trait_count[t]/collection.item_count
        c.trait_rarity[t] = 1/c.trait_freq[t]
        c.trait_rarity_normed[t] = c.trait_rarity[t]*(collection.get_avg_trait_per_cat()/len(c.traits))


# Loop over items and calculate statistical rarity and rarity score
for i in collection.items:
    for c, t in i.traits.items():
        i.stat_rarity = i.stat_rarity * collection.categories[c].trait_freq[t]
        i.rarity_score = i.rarity_score + collection.categories[c].trait_rarity[t]
        i.rarity_score_normed = i.rarity_score_normed + collection.categories[c].trait_rarity_normed[t]

# Open workbook for output to excel file, set up number formats
workbook = xlsxwriter.Workbook('../pudgypenguins.xlsx')
ws1 = workbook.add_worksheet("Items")
ws2 = workbook.add_worksheet("Categories")
bold = workbook.add_format({'bold': True})
percent = workbook.add_format({'num_format': 10})
# Write headers for sheet 1 - items
ws1.write(0, 0, "ID", bold)
for idx, t in enumerate(collection.categories.values()):
    ws1.write(0, 2*idx+1, t.name, bold)
    ws1.write(0, 2*idx+2, "Freq. (%)", bold)
ws1.write(0, len(collection.categories)*2+1, "Stat. rarity", bold)
ws1.write(0, len(collection.categories)*2+2, "Rarity score", bold)
ws1.write(0, len(collection.categories)*2+3, "Rarity score normed", bold)
# Write data to sheet 1
for idx, i in enumerate(collection.items):
    ws1.write(idx+1, 0, i.ID)
    for idx2, t in enumerate(collection.categories.values()):
        if i.traits[t.name]:
            ws1.write(idx+1, 2*idx2+1, i.traits[t.name])
        else:
            ws1.write(idx+1, 2*idx2+1, "None")
        ws1.write(idx+1, 2*idx2+2, collection.categories[t.name].trait_freq[i.traits[t.name]], percent)
    ws1.write(idx+1, len(i.traits)*2+1, i.stat_rarity)
    ws1.write(idx+1, len(i.traits)*2+2, i.rarity_score)
    ws1.write(idx+1, len(i.traits)*2+3, i.rarity_score_normed)
# Write headers for sheet 2
idx = 0                                 # Counter used for writing to ws2
cat_offset = 0                          # Keep track of counts from last category
ws2.write(0, 3, "# of cats", bold)
ws2.write(0, 4, len(collection.categories))
ws2.write(0, 6, "# of traits", bold)
ws2.write(0, 7, len(collection.traits))
ws2.write(0, 9, "Avg # in cat", bold)
ws2.write(0, 10, collection.get_avg_trait_per_cat())
ws2.write(0, 12, "Med # in cat", bold)
ws2.write(0, 13, collection.get_med_trait_per_cat())
ws2.write(0, 15, "GM # in cat", bold)
ws2.write(0, 16, collection.get_gm_trait_per_cat())
ws2.write(0, 18, "HM # in cat", bold)
ws2.write(0, 19, collection.get_hm_trait_per_cat())
for k, c in collection.categories.items():
    ws2.write(idx+cat_offset, 0, k, bold)
    ws2.write(idx+1+cat_offset, 0, "Rank")
    ws2.write(idx+1+cat_offset, 1, "Name")
    ws2.write(idx+1+cat_offset, 2, "Rarity Score")
    ws2.write(idx+1+cat_offset, 3, "Count")
    ws2.write(idx+1+cat_offset, 4, "Percent")
    ws2.write(idx+1+cat_offset, 5, "Rarity Score Normed")
    ws2.write(idx+1+cat_offset, 6, len(c.traits))
    for t in c.traits:
        ws2.write(idx+2+cat_offset, 0, "rank")
        ws2.write(idx+2+cat_offset, 1, t)
        ws2.write(idx+2+cat_offset, 2, c.trait_rarity[t])
        ws2.write(idx+2+cat_offset, 3, c.trait_count[t])
        ws2.write(idx+2+cat_offset, 4, c.trait_freq[t])
        ws2.write(idx+2+cat_offset, 5, c.trait_rarity_normed[t])
        idx += 1
    cat_offset += 2
workbook.close()

# Read in
df = pd.read_excel("./data/pudgypenguins.xlsx", engine='openpyxl')