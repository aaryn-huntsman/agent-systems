#!/usr/bin/env python3
"""Find-It demo dataset: Blue Ridge Outfitters, a fictional demo shop.

Every product, price, and guide below is invented for this demo and
labeled as such on the page. Descriptions are written the way good
product pages read — use cases, who it suits, conditions — because
that is the text a real store's semantic search would index.

Gold labels for the 8 preset shopper questions were chosen by hand:
each gold chunk is the product or guide a knowledgeable shop assistant
would actually point to, and the rationale says why.

Run: python3 dataset.py  ->  chunks.json, questions.json
"""
import json
from pathlib import Path

HERE = Path(__file__).parent

PRODUCTS = [
    # --- Footwear -------------------------------------------------------
    {"id": "prod-01", "name": "Ridgeline Mid Waterproof Hiking Boots", "category": "Footwear", "price": 139.95,
     "text": "Our best-selling all-rounder for day hikes and weekend backpacking on mixed terrain. A waterproof membrane keeps feet dry through creek crossings and muddy spring trails, while the cushioned midsole takes the sting out of long miles. Supportive around the ankle without feeling stiff, and broken-in comfortable almost straight from the box. A dependable first serious hiking boot."},
    {"id": "prod-02", "name": "Summit Wide-Fit Trail Boots", "category": "Footwear", "price": 159.95,
     "text": "Built on a genuinely wide last for hikers whose feet swell and splay over a long day — no more crushed toes or numb forefoot by mile ten. Extra cushioning under the heel and a rockered sole soften the pounding of steep, rocky descents, and the deep-lug outsole grips loose scree and wet stone. If standard boots leave your feet aching on the way down, these were made for you."},
    {"id": "prod-03", "name": "Featherstep Trail Runners", "category": "Footwear", "price": 119.95,
     "text": "For fast, light days on smooth trails when a boot feels like overkill. These breathable trail runners disappear on your foot, drain quickly after stream crossings, and grip well on packed dirt and gravel. Runners and speed hikers love them for high-mileage summer days. Not the pick for heavy packs or technical rock, but unbeatable when you want to move quickly and travel light."},
    {"id": "prod-04", "name": "Glacier GTX Insulated Winter Boots", "category": "Footwear", "price": 189.95,
     "text": "Serious warmth for winter trails: 400 grams of insulation rated to -25°F, a waterproof-breathable shell, and an outsole compound that stays grippy on packed snow and icy parking lots. Tall enough to keep snow out when the trail drifts over, with room for thick winter socks. Made for snowshoe approaches, winter summits, and anyone whose toes go numb by the trailhead."},
    # --- Shelter --------------------------------------------------------
    {"id": "prod-05", "name": "Aurora 2P Backpacking Tent", "category": "Tents & Shelter", "price": 249.95,
     "text": "A true two-person, three-season backpacking tent that splits to about two pounds per hiker. Two doors and two vestibules mean nobody climbs over a partner at 2 a.m., and the near-vertical walls give real shoulder room for two pads. Sets up fast with color-coded clips and shrugs off mountain downpours. The sweet spot for couples and partners starting multi-day trips."},
    {"id": "prod-06", "name": "Solstice 1P Ultralight Tent", "category": "Tents & Shelter", "price": 329.95,
     "text": "One pound fourteen ounces, total, for solo hikers who measure their kit in grams. This single-wall ultralight shelter pitches with your trekking poles, packs to the size of a loaf of bread, and still gives a six-footer room to sit up and change. Every zipper, stake, and seam was chosen to shave weight. For the solo backpacker counting every ounce, this is the shelter that makes the spreadsheet work."},
    {"id": "prod-07", "name": "Basecamp 6 Family Tent", "category": "Tents & Shelter", "price": 299.95,
     "text": "A drive-up campsite headquarters for families: standing height throughout, a screened porch for bug-free evenings, and room-darkening fabric that buys parents a precious extra hour of sleep after sunrise. Divides into two rooms so little ones can crash early while adults stay up. Straightforward pole setup two adults can manage in fifteen minutes, and it swallows air mattresses, a pack-and-play, and everyone's duffels."},
    {"id": "prod-08", "name": "Haven Hammock with Bug Net", "category": "Tents & Shelter", "price": 89.95,
     "text": "A gathered-end camping hammock with a fully enclosing no-see-um bug net, tree-friendly straps, and a ridgeline you can actually get a flat lay on. Packs down to softball size for summer backpacking in hardwood forests where flat tent sites are scarce. Blissful for afternoon naps at camp too. Needs two trees and a separate tarp if rain threatens."},
    # --- Sleep ----------------------------------------------------------
    {"id": "prod-09", "name": "Ember 20°F Down Sleeping Bag", "category": "Sleep", "price": 219.95,
     "text": "850-fill down rated to 20°F for three-season backpacking in the mountains, where nights drop below freezing well into spring. A draft collar and shaped hood seal in warmth, and it compresses to the size of a bread loaf in your pack. The workhorse bag for anyone building a real backpacking kit who expects cold nights at altitude."},
    {"id": "prod-10", "name": "Drift 30°F Ultralight Quilt", "category": "Sleep", "price": 189.95,
     "text": "A backpacking quilt that ditches the zipper and the insulation underneath you — the parts a sleeping pad makes redundant — to land at just over a pound. Snaps and a drawcord footbox let you vent on warm nights or cinch down when it dips toward freezing. Thru-hikers and gram-counters pair it with an insulated pad for a sleep system lighter than most single bags."},
    {"id": "prod-11", "name": "Sprout Kids' Sleeping Bag", "category": "Sleep", "price": 59.95,
     "text": "A kids' bag that adjusts as they grow: an extension zipper adds length for several seasons of use, so you are not buying a new bag every summer. Rated to 30°F for campground nights, with a soft brushed lining, a glow-in-the-dark zipper pull little hands can find, and synthetic fill that still insulates after a spilled juice box. Sized for kids roughly four to ten."},
    {"id": "prod-12", "name": "Cloudrest Insulated Sleeping Pad", "category": "Sleep", "price": 79.95,
     "text": "Four inches of quiet, insulated comfort that keeps the cold ground from stealing your warmth — an R-value of 4.5 makes it a true three-season pad. Inflates with a pump sack so you are not dizzy at altitude, and the fabric is noticeably quieter than crinkly ultralight pads. The single cheapest upgrade to sleeping well outdoors, whatever bag you already own."},
    # --- Packs ----------------------------------------------------------
    {"id": "prod-13", "name": "Traverse 65L Backpacking Pack", "category": "Packs", "price": 179.95,
     "text": "A 65-liter hauler for week-long trips and winter loads, with an adjustable torso and a hip belt that actually carries the weight on your hips instead of your shoulders. Big front pocket swallows a wet tent, and the lid converts to a daypack for summit pushes. Comfortable at forty pounds, which is where lesser packs start to complain."},
    {"id": "prod-14", "name": "Ridgeday 20L Daypack", "category": "Packs", "price": 64.95,
     "text": "The grab-and-go pack for day hikes, travel days, and campus: twenty liters for layers, lunch, and two water bottles, with a padded sleeve that fits a 15-inch laptop. Breathable back panel for humid summer trails, and it stuffs into its own pocket when you need a spare bag on a trip. Simple, tough, and priced to be a first pack."},
    {"id": "prod-15", "name": "Hauler 70L Expedition Duffel", "category": "Packs", "price": 99.95,
     "text": "A burly duffel that swallows boots, helmets, and a week of expedition gear and shrugs off being tossed in truck beds and airport belts. Stowable backpack straps for long carries, lockable zippers, and a water-resistant base for wet tarmac. The bag guides and gear junkies reach for when everything has to fit in one place."},
    # --- Paddling -------------------------------------------------------
    {"id": "prod-16", "name": "Harbor Adult Life Vest", "category": "Paddling", "price": 74.95,
     "text": "A Coast Guard-approved life vest designed for paddlers: high-cut back that clears a kayak seat, open sides for unrestricted strokes, and three adjustable straps for a snug, ride-up-free fit. This is the first thing a new kayaker should buy — before the paddle, before the roof rack — and at under eighty dollars there is no excuse to skip it. Sizes run true; size up for layering in cold water."},
    {"id": "prod-17", "name": "Eddy Current Kayak Paddle", "category": "Paddling", "price": 89.95,
     "text": "A lightweight fiberglass-shaft paddle that takes the fatigue out of long lake days. The asymmetrical blades pull smoothly without flutter, and the two-piece design breaks down for the trunk. A real step up from bargain aluminum paddles — your shoulders will notice by hour three. Sized for recreational kayaks and calm to moderate water."},
    {"id": "prod-18", "name": "Dry Bag Duo — 10L & 20L", "category": "Paddling", "price": 34.95,
     "text": "Two roll-top dry bags that keep a phone, wallet, spare layer, and lunch genuinely dry — not water-resistant, dry — through splashes, rain, and the occasional capsize. The 10L rides between your feet in a kayak; the 20L handles group gear on a raft. Cheap insurance every paddler and rainy-day backpacker ends up wishing they had bought sooner."},
    {"id": "prod-19", "name": "Splash Youth Life Vest", "category": "Paddling", "price": 49.95,
     "text": "A Coast Guard-approved vest sized for kids 50–90 pounds, with a grab handle on the back for quick assists, a crotch strap that keeps it from riding up, and bright panels you can spot across a lake. Comfortable enough that kids actually keep it on — the fit is soft around the neck and arms. Required gear for young paddlers and boat days."},
    # --- Clothing & layers ----------------------------------------------
    {"id": "prod-20", "name": "Northwall Insulated Camp Jacket", "category": "Clothing", "price": 149.95,
     "text": "A lofty synthetic-insulated jacket built for the stopped hours: belays, summit lunches, and sitting around camp after the sun drops. It is deliberately over-warm for hiking uphill — this is the layer you pull on the moment you stop moving, and it turns a shivering dinner into a comfortable one. Packs into its own pocket, shrugs off light drizzle, and layers under a shell when the cold gets serious."},
    {"id": "prod-21", "name": "Meridian Merino Base Layer Top", "category": "Clothing", "price": 84.95,
     "text": "A midweight merino wool base layer that regulates temperature across a startling range and can be worn for days without smelling like it. Wicks sweat on the climb, insulates when you stop, and never gets that clammy synthetic chill. The foundation of any winter layering system — and soft enough that most people end up wearing it around town all season."},
    {"id": "prod-22", "name": "Stormline 3L Rain Shell", "category": "Clothing", "price": 169.95,
     "text": "A three-layer waterproof-breathable shell built for multi-day rain, not parking-lot showers. Fully taped seams, pit zips for dumping heat on climbs, a helmet-compatible hood that actually turns with your head, and a membrane rated to keep you dry through day three of a front. When the forecast says rain all weekend and you are going anyway, this is the jacket that makes the trip still fun."},
    {"id": "prod-23", "name": "Stormline Rain Pants", "category": "Clothing", "price": 119.95,
     "text": "Full-zip waterproof pants that go on over boots when the trail turns to a stream. The other half of staying dry on multi-day treks: a shell jacket alone leaves your legs soaked, your boots flooded from above, and your morale gone by lunch. Breathable, packable to grapefruit size, and reinforced at the cuff for crampon and brush abuse."},
    {"id": "prod-24", "name": "Trailhead Fleece Midlayer", "category": "Clothing", "price": 99.95,
     "text": "A grid fleece that does the unglamorous work of winter hiking: it breathes on the climb so you do not overheat, then traps warmth under a shell when the wind picks up. Athletic fit layers cleanly, thumbholes keep sleeves in place, and it is the layer experienced hikers reach for daily from November to March. Also the most-gifted item in our store, three winters running."},
    {"id": "prod-25", "name": "Sunridge UPF 50 Sun Hoodie", "category": "Clothing", "price": 54.95,
     "text": "A featherlight sun hoodie with UPF 50 protection for alpine lakes, desert trails, and long days on the water where sunscreen alone loses. The hood covers neck and ears, thumbholes extend coverage to the backs of your hands, and the fabric dries in minutes after a swim. A summer staple for fair-skinned hikers and paddlers."},
    # --- Winter ---------------------------------------------------------
    {"id": "prod-26", "name": "Traverse Microspikes Traction", "category": "Winter", "price": 69.95,
     "text": "Chains-and-spikes traction that stretches over your boots and turns icy trails from a slip-and-slide into a normal walk. Stainless spikes bite on packed snow, frozen mud, and the glare ice that forms on popular winter trails — the difference between turning around at the first frozen creek and finishing the hike. Packs tiny, goes on in seconds, and is the single most useful winter hiking upgrade under seventy dollars."},
    {"id": "prod-27", "name": "Powderline Snowshoes", "category": "Winter", "price": 129.95,
     "text": "Modern aluminum-frame snowshoes that keep you on top of deep snow instead of postholing to your knees. Aggressive crampons grip traverses and icy crust, and the bindings cinch with gloves on. Rated for users up to 200 pounds with a winter pack. For rolling forest trails, frozen lakes, and breaking trail to the backcountry hut."},
    {"id": "prod-28", "name": "Frostbite Merino Balaclava", "category": "Winter", "price": 34.95,
     "text": "A merino balaclava that covers the cheeks, nose, and neck a hat leaves exposed, with a hinged design that pulls down when you need to breathe hard or sip water. Windproof panel across the forehead for ridge days. Small, cheap, and the difference between enjoying a windy summit and hiding from it."},
    # --- Cooking --------------------------------------------------------
    {"id": "prod-29", "name": "Jetstream Canister Stove", "category": "Cooking", "price": 59.95,
     "text": "A pocket-sized canister stove that boils a liter of water in about three minutes — fast enough that coffee happens before the tent even comes down. Simmer control is genuinely usable for actual cooking, the pot supports fold flat, and it lights reliably in cold morning air when lesser stoves sputter. The backpacking stove most people end up recommending to their friends."},
    {"id": "prod-30", "name": "Titan Titanium Pot Set", "category": "Cooking", "price": 74.95,
     "text": "A nesting titanium pot-and-lid set that weighs almost nothing and will outlast every other piece of your kit. The 1.4-liter pot handles pasta for two; the lid doubles as a small pan. Titanium heats fast and cleans easily, though it scorches delicate sauces — this set is for boiling, rehydrating, and simple one-pot meals at camp."},
    {"id": "prod-31", "name": "Basecamp Two-Burner Camp Stove", "category": "Cooking", "price": 119.95,
     "text": "A classic two-burner propane stove for car camping: pancakes on one side, coffee percolating on the other, and enough windscreen to keep flames alive on a breezy lakeshore. Fits a family-size griddle, folds flat for the car, and runs on standard one-pound canisters. This is the stove behind a thousand campground breakfasts."},
    {"id": "prod-32", "name": "Ember Steel Camp Mug — 16oz", "category": "Cooking", "price": 24.95,
     "text": "A double-wall insulated steel mug that keeps coffee hot through a frosty sunrise and cocoa warm through campfire stories. Fits most cup holders for the drive to the trailhead, with a press-on lid that slows spills. Nearly indestructible, and the small luxury every camp kitchen deserves."},
    # --- Safety, light, navigation --------------------------------------
    {"id": "prod-33", "name": "Lumen 400 Headlamp", "category": "Safety & Light", "price": 44.95,
     "text": "Four hundred lumens with a red night-vision mode, a lockout so it does not die in your pack, and USB-C recharging. Bright enough for night navigation on trail, dimmable enough for reading in the tent without blinding your partner. A headlamp is on every ten-essentials list for a reason — this one covers dawn starts, late descents, and midnight trips to the bear hang."},
    {"id": "prod-34", "name": "TrailSafe First Aid Kit", "category": "Safety & Light", "price": 39.95,
     "text": "A trail first aid kit organized the way emergencies actually happen: blister care up front, then wound care, medications, and tools, each in labeled compartments you can navigate with cold hands. Includes moleskin, an irrigation syringe, tweezers, and a compact emergency blanket. Sized for a daypack and stocked for the injuries day hikers actually get."},
    {"id": "prod-35", "name": "Waypoint Handheld GPS", "category": "Safety & Light", "price": 249.95,
     "text": "A rugged handheld GPS with preloaded topo maps, multi-satellite positioning that holds a fix in deep canyons and heavy tree cover, and a barometric altimeter for tracking weather trends. Battery runs for a week of backpacking, and waypoints sync with your phone when you are back in range. For off-trail travel where a phone signal is a rumor."},
    # --- Family ---------------------------------------------------------
    {"id": "prod-36", "name": "Cub Carrier Child Hiking Pack", "category": "Family", "price": 159.95,
     "text": "A framed child carrier that lets toddlers ride in comfort on real hikes: padded cockpit, adjustable stirrups, a sunshade, and a hip belt that puts the load on the adult's hips where it belongs. Stands on its own for loading, with storage for diapers, snacks, and a layer for two. For kids who can sit up unassisted, roughly six months to three years — the pack that keeps hiking in a young family's life."},
]

GUIDES = [
    {"id": "guide-01", "name": "Gift Guide: For the New Winter Hiker", "category": "Buying Guide",
     "text": "Shopping for someone who just discovered winter hiking? Skip the novelty gear and give the things experienced winter hikers actually carry. Traction comes first: a set of boot microspikes turns icy trails safe and is the gift new winter hikers thank you for all season. Next, a warm midlayer — a grid fleece gets worn on nearly every cold-weather hike and layers under any shell. Round it out with merino: a base layer or balaclava feels luxurious, always fits the layering system, and never goes unused. Finish with the small stuff — a bright headlamp for short winter days and an insulated mug for trailhead coffee. Everything on this list is under $100 except the boots, and all of it earns its place in a winter pack."},
    {"id": "guide-02", "name": "Getting Started: Beginner Kayaking Essentials", "category": "Buying Guide",
     "text": "New to kayaking? Here is the honest order to buy things in. First, before anything else, a properly fitted life vest made for paddling — it is the one piece of gear that can save your life, it is legally required in most places, and a good one costs less than a tank of gas. Second, a paddle that fits your height; a lightweight one prevents the shoulder fatigue that ends beginner days early. Third, a dry bag for your phone, keys, and a spare layer, because you will get splashed and you might swim. Add a whistle, a bilge sponge, and a plan to stay near shore while you learn. Rent the boat itself for your first few outings — once you know you love it, you will know what kind of kayak to buy."},
    {"id": "guide-03", "name": "Winter Hiking Layers, Explained", "category": "Buying Guide",
     "text": "Winter layering is a system of three jobs. The base layer, worn against the skin, moves sweat away so it cannot chill you — merino wool is the favorite because it insulates while damp and resists odor for days. The mid layer traps warmth: a breathable grid fleece for moving, a puffy insulated jacket for stops. The shell blocks wind and precipitation; it does not need to be waterproof for dry, cold days, but it must cut wind completely. The rules that make it work: never wear cotton, start the hike slightly cold so you do not sweat through your layers in the first mile, and add or shed a layer before you get hot or cold, not after. Hands, head, and feet get their own attention — most winter misery starts at the extremities."},
    {"id": "guide-04", "name": "Your First Camping Kit: The Honest Checklist", "category": "Buying Guide",
     "text": "Your first camping trip does not need a specialty store's worth of gear — it needs the few things that decide whether you sleep well and stay comfortable. Shelter first: a tent with room to sit up and a rainfly that reaches the ground. Sleep second, and do not skimp backwards: a sleeping pad matters more than the bag, because the ground steals more heat than the air. Third, light — a headlamp each, not a lantern to share. Fourth, simple food and a way to heat water; a two-burner stove and one pot cover most campground cooking. Bring camp chairs, a cooler, and more blankets than seems reasonable if you are car camping with little kids. Borrow or rent the rest, go once, and let the trip itself tell you what to buy next."},
]

QUESTIONS = [
    {"q": "a gift for my dad who just got into winter hiking",
     "gold": {"guide-01": "The gift guide is written for exactly this shopper — someone buying for a new winter hiker — and names specific gifts.",
              "prod-26": "Microspikes are the guide's first-named gift and the classic under-$70 winter hiking present: useful on every icy trail."}},
    {"q": "something to keep a beginner kayaker safe under $100",
     "gold": {"prod-16": "The adult life vest is the safety-first purchase for a new kayaker, Coast Guard-approved and $74.95 — inside the $100 budget.",
              "guide-02": "The beginner kayaking guide puts the life vest first, before paddle or boat, for exactly this reason."}},
    {"q": "our toddler's first camping trip",
     "gold": {"prod-07": "The family tent is built for this: standing room, a room divider so little ones can sleep early, and space for a pack-and-play.",
              "guide-04": "The first camping kit checklist covers camping with little kids specifically — extra blankets, a headlamp each, simple food."}},
    {"q": "boots for wide feet that won't ache on long rocky descents",
     "gold": {"prod-02": "The Summit boots are built on a wide last with extra cushioning aimed at exactly the forefoot ache of long rocky descents."}},
    {"q": "a warm layer for sitting around camp at night, not for moving in",
     "gold": {"prod-20": "The Northwall jacket is explicitly built for the stopped hours — belays and camp evenings — and described as over-warm for hiking uphill."}},
    {"q": "lightweight kit for a solo backpacker counting every ounce",
     "gold": {"prod-06": "The Solstice is a 1 lb 14 oz solo shelter pitched with trekking poles, written for gram-counters.",
              "prod-10": "The Drift quilt is the other half of the ultralight sleep system at just over a pound, aimed at thru-hikers and gram-counters."}},
    {"q": "staying dry through days of rain on the trail",
     "gold": {"prod-22": "The Stormline shell is a three-layer waterproof built for multi-day rain, not parking-lot showers.",
              "prod-23": "The matching rain pants are described as the other half of staying dry on multi-day treks."}},
    {"q": "a fast-boiling stove for coffee on cold mornings",
     "gold": {"prod-29": "The Jetstream boils a liter in about three minutes and is framed around camp coffee before the tent comes down."}},
]


def main():
    chunks = ([{"id": p["id"], "kind": "product", "name": p["name"], "category": p["category"],
                "price": p["price"], "text": p["text"]} for p in PRODUCTS]
              + [{"id": g["id"], "kind": "guide", "name": g["name"], "category": g["category"],
                  "price": None, "text": g["text"]} for g in GUIDES])
    (HERE / "chunks.json").write_text(json.dumps(chunks, indent=1), encoding="utf-8")
    (HERE / "questions.json").write_text(json.dumps(QUESTIONS, indent=1), encoding="utf-8")
    print(f"{len(chunks)} chunks ({len(PRODUCTS)} products, {len(GUIDES)} guides), {len(QUESTIONS)} questions")


if __name__ == "__main__":
    main()
