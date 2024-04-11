import csv
import sys

# Deal with large record sizes
csv.field_size_limit(sys.maxsize)

# Keywords and their scores
club_keywords = {
    'club': 10, 'organisation': 9, 'guild': 9, 'society': 9,
    'association': 7, 'company': 5, 'league': 9, 'union': 8
}
event_keywords = {
    'event': 10, 'experience': 6, 'occasion': 7, 'adventure': 5, 'function': 5
}

# Threshold score
threshold_score = 20  # Adjustable

# File names
input_file = 'locaria.all_items.csv'
club_file = 'club.csv'
club_possible_file = 'club_possible.csv'
events_possible_file = 'events_possible.csv'
failures_file = 'failures.csv'

# Record counters
counters = {'club': 0, 'club_possible': 0, 'events_possible': 0, 'failures': 0}

# Score calculation function
def calculate_scores(text):
    club_score = sum(score for keyword, score in club_keywords.items() if keyword in text.lower())
    event_score = sum(score for keyword, score in event_keywords.items() if keyword in text.lower())
    return club_score, event_score

# Process records
with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    
    # Prepare output files
    with open(club_file, mode='w', newline='', encoding='utf-8') as club_out, \
         open(club_possible_file, mode='w', newline='', encoding='utf-8') as club_possible_out, \
         open(events_possible_file, mode='w', newline='', encoding='utf-8') as events_possible_out, \
         open(failures_file, mode='w', newline='', encoding='utf-8') as failures_out:

        # Write headers
        fieldnames = reader.fieldnames + ['club_score', 'event_score', 'final_score']
        club_writer = csv.DictWriter(club_out, fieldnames=fieldnames)
        club_possible_writer = csv.DictWriter(club_possible_out, fieldnames=fieldnames)
        events_possible_writer = csv.DictWriter(events_possible_out, fieldnames=fieldnames)
        failures_writer = csv.DictWriter(failures_out, fieldnames=fieldnames)
        for writer in [club_writer, club_possible_writer, events_possible_writer, failures_writer]:
            writer.writeheader()
        
        # Process each record
        for row in reader:
            text = f"{row['title']} {row['description']}"
            club_score, event_score = calculate_scores(text)
            final_score = 2 * club_score + event_score
            row.update({'club_score': club_score, 'event_score': event_score, 'final_score': final_score})
            
            # Determine which file to write to based on scores
            if final_score >= threshold_score:
                club_writer.writerow(row)
                counters['club'] += 1
            elif final_score < threshold_score and club_score >= event_score:
                club_possible_writer.writerow(row)
                counters['club_possible'] += 1
            elif final_score < threshold_score and club_score < event_score:
                events_possible_writer.writerow(row)
                counters['events_possible'] += 1
            else:
                failures_writer.writerow(row)
                counters['failures'] += 1

# Print summary
print("Summary of record counts for each file:")
for key, count in counters.items():
    print(f"{key}: {count}")