import csv
import sys


def main():

    # Check for command-line usage
    if len(sys.argv) != 3:
        sys.exit(1)
    db_name = sys.argv[1]
    s_file = sys.argv[2]

    # Read database file into a variable
    with open(db_name, 'r') as db:
        reader = csv.DictReader(db)
        people = []
        genes = reader.fieldnames[1:]
        for row in reader:
            people.append(row)

    #  Read DNA sequence file into a variable

    with open(s_file, 'r') as file:
        sequence = file.read()
    sequence = sequence.strip()

    #  Find longest match of each STR in DNA sequence
    data = {}
    for gen in genes:
        data[gen] = longest_match(sequence=sequence, subsequence=gen)

    #  Check database for matching profiles
    for person in people:
        match = True
        for gen in person:
            if gen == 'name':
                continue  # next key
            if int(person[gen]) != data[gen]:
                match = False
                break

        if match:
            print(person['name'])
            break

    if not match:
        print('No match')

    return


def longest_match(sequence, subsequence):
    """Returns length of longest run of subsequence in sequence."""

    # Initialize variables
    longest_run = 0
    subsequence_length = len(subsequence)
    sequence_length = len(sequence)

    # Check each character in sequence for most consecutive runs of subsequence
    for i in range(sequence_length):

        # Initialize count of consecutive runs
        count = 0

        # Check for a subsequence match in a "substring" (a subset of characters) within sequence
        # If a match, move substring to next potential match in sequence
        # Continue moving substring and checking for matches until out of consecutive matches
        while True:

            # Adjust substring start and end
            start = i + count * subsequence_length
            end = start + subsequence_length

            # If there is a match in the substring
            if sequence[start:end] == subsequence:
                count += 1

            # If there is no match in the substring
            else:
                break

        # Update most consecutive matches found
        longest_run = max(longest_run, count)

    # After checking for runs at each character in seqeuence, return longest run found
    return longest_run


main()
