from __future__ import print_function
import freesound
import os
import sys


def createClient():
    api_key = os.getenv('FREESOUND_API_KEY', "xbdYSYi9lDMRwSekK8ThcIAe7gserici1pz0VoPe")
    if api_key is None:
        print("You need to set your API key as an evironment variable", )
        print("named FREESOUND_API_KEY")
        sys.exit(-1)

    freesound_client = freesound.FreesoundClient()
    freesound_client.set_token(api_key)

    return freesound_client

def printpage1(results):
    for sound in results:
        print("\t-", sound.name, "by", sound.username)

def filter_options():
    print("""
        Filter Name		    Type		Description
        id			        integer		Sound ID on Freesound.
        username		    string		Username of the sound uploader (not tokenized).
        created		        date		Date in which the sound was added to Freesound (see date example filters below).
        original_filename	string		Name given to the sound (tokenized).
        description		    string		Textual description given to the sound (tokenized).
        tag			        string		Tag +
        license			    string		Name of the Creative Commons license, one of[“Attribution”, “Attribution Noncommercial”, “Creative Commons 0”]. f 
        is_remix		    boolean	    Whether the sound is a remix of another Freesound sound.
        was_remixed		    boolean	    Whether the sound has remixes in Freesound.
        type			    string		Original file type, one off [“wav”, “aiff”, “ogg”, “mp3”, “m4a”, “flac”]. ?
        duration		    numerical	Duration of sound in seconds. + 
        samplerate		    integer		Samplerate. {fields}
        filesize			integer		File size in bytes.
        channels		    integer		Number of channels in sound (mostly 1 or 2). !
        num_downloads	    integer		Number of times the sound has been downloaded.
        avg_rating		    numerical	Average rating for the sound in the range [0, 5].
        num_ratings		    integer		Number of times the sound has been rated.
        
        Filters are defined with a syntax like fieldname:value fieldname:value
        For numeric or integer filters, a range can also be specified using
        fieldname:[start TO end]
        fieldname:[* TO end]
        fieldname:[start to *]
        
        Simple logic operators can also be used
        type:(wav OR aiff)
        description:(piano AND note)
        
    """)


def textSearch():
    client = createClient()
    data = input("TEXT SEARCH\nWhich kind of sound do you want to download? ")
    ask = input("Do you want to apply some filters to your initial query? Type yes or no ")
    if ask == "yes":
        filter_options()
        f = input("Add the filters you want with their corresponding data type.\n")
        print("Looking for " + data + " sounds filtered by " + f)
        results = client.text_search(
            query=data,
            sort="score",
            fields="id,name,username",
            filter=f  #"is_remix:true, channels:1"
        )
        printpage1(results)
    elif ask == "no":
        print("Looking for " + data)
        results = client.text_search(
            query=data,
            sort="score",
            fields="id,name,username",
        )
        printpage1(results)
    else:
        print("Please type yes or no.")
        textSearch()

def descriptors_options():
    print(""" 
Descriptors are defined with syntax like descriptor_name:value 
Moreover, if used with statistics the syntax is descriptor_name.stats:value 
value can include numeric ranges and simple logic operators 
descriptor:[start TO end]       descriptor:[* TO end]       descriptor:[start to *]
descriptor:(a OR b)             descriptor:(A AND b)

There are four types of descriptors, of which some of them can be used with statistics
        """)


def lowleveldescriptors():
    print(""" 
        LOW LEVEL DESCRIPTORS
        Generally, the lowlevel descriptors have the statistics mean, max, min, var, dmean, dmean2, dvar, and dvar2.
        
        lowlevel.spectral_complexity
        lowlevel.silence_rate_20dB
        lowlevel.erb_bands
        lowlevel.average_loudness
        lowlevel.spectral_rms
        lowlevel.spectral_kurtosis
        lowlevel.barkbands_kurtosis
        lowlevel.scvalleys
        lowlevel.spectral_spread
        lowlevel.pitch
        lowlevel.dissonance
        lowlevel.spectral_energyband_high
        lowlevel.gfcc
        lowlevel.spectral_flux
        lowlevel.silence_rate_30dB
        lowlevel.spectral_contrast
        lowlevel.spectral_energyband_middle_high
        lowlevel.barkbands_spread
        lowlevel.spectral_centroid
        lowlevel.pitch_salience
        lowlevel.silence_rate_60dB
        lowlevel.spectral_entropy
        lowlevel.spectral_rolloff
        lowlevel.barkbands
        lowlevel.spectral_energyband_low
        lowlevel.barkbands_skewness
        lowlevel.pitch_instantaneous_confidence
        lowlevel.spectral_energyband_middle_low
        lowlevel.spectral_strongpeak
        lowlevel.startFrame
        lowlevel.spectral_decrease
        lowlevel.stopFrame
        lowlevel.mfcc
        lowlevel.spectral_energy
        lowlevel.spectral_flatness_db
        lowlevel.frequency_bands
        lowlevel.zerocrossingrate
        lowlevel.spectral_skewness
        lowlevel.hfc
        lowlevel.spectral_crest
        """)

#fuera
def rhythmdescriptors():
    print(""" 
        RHYTHM DESCRIPTORS
        rhythm.first_peak_bpm
        rhythm.onset_times
        rhythm.beats_count
        rhythm.beats_loudness
        rhythm.first_peak_spread
        rhythm.second_peak_weight
        rhythm.bpm
        rhythm.bpm_intervals
        rhythm.onset_count
        rhythm.second_peak_spread
        rhythm.beats_loudness_band_ratio
        rhythm.second_peak_bpm
        rhythm.onset_rate
        rhythm.beats_position
        rhythm.first_peak_weight
        """)

def tonaldescriptors():
    print(""" 
        TONAL DESCRIPTORS
        tonal.hpcp_entropy
        tonal.chords_scale
        tonal.chords_number_rate
        tonal.key_strength
        tonal.chords_progression
        tonal.key_scale
        tonal.chords_strength
        tonal.key_key
        tonal.chords_changes_rate
        tonal.chords_count
        tonal.hpcp_crest
        tonal.chords_histogram
        tonal.chords_key
        tonal.tuning_frequency
        tonal.hpcp_peak_count
        tonal.hpcp
        """)

#fuera
def sfxdescriptors():
    print(""" 
        SFX DESCRIPTORS
        sfx.temporal_decrease
        sfx.inharmonicity
        sfx.pitch_min_to_total
        sfx.tc_to_total
        sfx.der_av_after_max
        sfx.pitch_max_to_total
        sfx.temporal_spread
        sfx.temporal_kurtosis
        sfx.logattacktime
        sfx.temporal_centroid
        sfx.tristimulus
        sfx.max_der_before_max
        sfx.strongdecay
        sfx.pitch_centroid
        sfx.duration
        sfx.temporal_skewness
        sfx.effective_duration
        sfx.max_to_total
        sfx.oddtoevenharmonicenergyratio
        sfx.pitch_after_max_to_before_max_energy_ratio
        """)

def statistics():
    print("""  
        mean	The arithmetic mean
        max	    The maximum value
        min	    The minimum value
        var	    The variance
        dmean	The mean of the derivative
        dmean2	The mean of the second derivative
        dvar	The variance of the derivative
        dvar2	The variance of the second derivative
        """)

def printdescriptors():
    descriptors_options()
    menu = {'1': "Show Lowlevel Descriptors", '2': "Show Rhythm Descriptors", '3': "Show Tonal Descriptors", '4': "Show Sfx Descriptors", '5': "Show stats", '6': "Next step"}
    loop = True
    while loop:
        for entry in menu:
            print(entry, menu[entry])
        selection = input("Please select to see the specified descriptors: ")
        if selection == '1':
            lowleveldescriptors()
        elif selection == '2':
            rhythmdescriptors()
        elif selection == '3':
            tonaldescriptors()
        elif selection == '4':
            sfxdescriptors()
        elif selection == '5':
            statistics()
        elif selection == '6':
            loop = False
        else:
            print("Unknown Option Selected!")

#Note that if target (or analysis_file) is not used in combination with descriptors_filter,
# the results of the query will include all sounds from Freesound indexed in the similarity server,
# sorted by similarity to the target.
def contentSearch():
    client = createClient()
    print("CONTENT SEARCH")
    printdescriptors()
    t = input("TARGET defines a target based on content-based descriptors to sort the search results. \nIt can be set as a number of descriptor name and value pairs, or as a sound id.\nSet your target: ")
    df = input("DESCRIPTORS FILTER  is used to restrict the query results to those sounds whose content descriptor values match with the defined filter.\nSet your descriptor filters ")
    results = client.content_based_search(
        target=t, #"lowlevel.pitch.mean:220",
        descriptors_filter = df, #"lowlevel.pitch_instantaneous_confidence.mean:[0.8 TO 1]",
        sort="score",
        fields="id,name,username"
    )
    printpage1(results)


def combinedSearch2():
    client = createClient()
    q = input("query: ")
    df = input("descriptors filter: ")
    results = client.combined_search(
        query=q,
        descriptors_filter=df,
        sort="score"

    )
    printpage1(results)


def combinedSearch3():
    client = createClient()
    q = input("query: ")
    df = input("descriptors filter: ")
    f = input("filter: ")
    results = client.combined_search(
        query=q,
        descriptors_filter=df,
        filter=f,
        sort="score"
    )
    printpage1(results)


def combinedSearch4():
    client = createClient()
    t = input("target: ")
    f = input("filter: ")
    results = client.combined_search(
        target=t,
        filter=f,
        sort="score"
    )
    printpage1(results)


def combinedSearch6():
    client = createClient()
    t = input("target: ")
    df = input("descriptors filter: ")
    f = input("filter: ")
    results = client.combined_search(
        target=t,
        descriptors_filter=df,
        filter=f,
        sort="score"
    )
    printpage1(results)


def combinedSearch():
    print("""
This resource is a combination of Text Search and Content Search
To perform a Combined Search query you must at least specify a query or a target parameter (can not be used at the same time), 
and at least one text-based or content-based filter (filter and descriptors_filter)
Request parameters query and target can not be used at the same time, 
but filter and descriptors filter can both be present in a single Combined Search query

The proposed combined searches are
1. query + filter
2. query + descriptor filter
3. query + filter + descriptor filter
4. target + filter
5. target + descriptor filter
6. target + filter + descriptor filter
    """)
    selection = input("Please select an option: ")
    if selection == '1':
        textSearch()
    elif selection == '2':
        combinedSearch2()
    elif selection == '3':
        combinedSearch3()
    elif selection == '4':
        combinedSearch4()
    elif selection == '5':
        contentSearch()
    elif selection == '6':
        combinedSearch6()
    else:
        print("Unknown Option Selected!")
        combinedSearch()


def menu():
    menu = {'1': "Text Search", '2': "Content Search", '3': "Combined Search", '4': "Exit"}
    while True:
        for entry in menu:
            print(entry, menu[entry])

        selection = input("Please Select: ")
        if selection == '1':
            textSearch()
        elif selection == '2':
            contentSearch()
        elif selection == '3':
            combinedSearch()
        elif selection == '4':
            break
        else:
            print("Unknown Option Selected!")

menu()



"""
# Get sound info example
print("Sound info:")
print("-----------")
sound = freesound_client.get_sound(96541)
print("Getting sound:", sound.name)
print("Url:", sound.url)
print("Description:", sound.description)
print("Tags:", " ".join(sound.tags))
print()

sound.retrieve("/data")



# Get sound info example specifying some request parameters
print("Sound info specifying some request parameters:")
print("-----------")
sound = freesound_client.get_sound(
    96541,
    fields="id,name,username,duration,analysis",
    descriptors="lowlevel.spectral_centroid",
    normalized=1
)

print("Getting sound:", sound.name)
print("Username:", sound.username)
print("Duration:", str(sound.duration), "(s)")
print("Spectral centroid:",)
print(sound.analysis.lowlevel.spectral_centroid.as_dict())
print()

# Get sound analysis example
print("Get analysis:")
print("-------------")
analysis = sound.get_analysis()

mfcc = analysis.lowlevel.mfcc.mean
print("Mfccs:", mfcc)
# you can also get the original json (this apply to any FreesoundObject):
print(analysis.as_dict())
print()

# Get sound analysis example specifying some request parameters
print("Get analysis with specific normalized descriptor:")
print("-------------")
analysis = sound.get_analysis(
    descriptors="lowlevel.spectral_centroid.mean",
    normalized=1
)
spectral_centroid_mean = analysis.lowlevel.spectral_centroid.mean
print("Normalized mean of spectral centroid:", spectral_centroid_mean)
print()

# Get similar sounds example
print("Similar sounds: ")
print("---------------")
results_pager = sound.get_similar()
for similar_sound in results_pager:
    print("\t-", similar_sound.name, "by", similar_sound.username)
print()

# Get similar sounds example specifying some request parameters
print("Similar sounds specifying some request parameters:")
print("---------------")
results_pager = sound.get_similar(
    page_size=10,
    fields="name,username",
    descriptors_filter="lowlevel.pitch.mean:[110 TO 180]"
)
for similar_sound in results_pager:
    print("\t-", similar_sound.name, "by", similar_sound.username)
print()

# Search Example
print("Searching for 'violoncello':")
print("----------------------------")
results_pager = freesound_client.text_search(
    query="violoncello",
    filter="tag:tenuto duration:[1.0 TO 15.0]",
    sort="rating_desc",
    fields="id,name,previews,username"
)
print("Num results:", results_pager.count)
print("\t----- PAGE 1 -----")
for sound in results_pager:
    print("\t-", sound.name, "by", sound.username)
print("\t----- PAGE 2 -----")
results_pager = results_pager.next_page()
for sound in results_pager:
    print("\t-", sound.name, "by", sound.username)
print()

# Content based search example
print("Content based search:")
print("---------------------")
results_pager = freesound_client.content_based_search(
    descriptors_filter="lowlevel.pitch.var:[* TO 20]",
    target='lowlevel.pitch_salience.mean:1.0 lowlevel.pitch.mean:440'
)

print("Num results:", results_pager.count)
for sound in results_pager:
    print("\t-", sound.name, "by", sound.username)
print()


"""

