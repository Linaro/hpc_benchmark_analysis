#!/usr/bin/env perl

use strict;
use warnings;
use Data::Dumper;

my $SYNTAX = "Syntax: $0 <results-dir>\n";

my $DIR = $ARGV[0];
die $SYNTAX unless (-d $DIR);
opendir (DIR, $DIR) || die "Can't open dir $DIR: !$\n";
my @FILES = grep { /^[^\.]/ } readdir(DIR);
closedir(DIR);
$DIR =~ s/\/+$//;

# Initialise global data
# TODO: Decouple and merge with find_create_hash()
my %DATA = ();
$DATA{'meta'} = {};
$DATA{'meta'}->{'common'} = {};
my $common = $DATA{'meta'}->{'common'};
$DATA{'meta'}->{'data_tags'} = {};
my $data_tags = $DATA{'meta'}->{'data_tags'};
$DATA{'meta'}->{'categories'} = {};
my $categories = $DATA{'meta'}->{'categories'};
$DATA{'meta'}->{'comparison'} = {};
my $comparison = $DATA{'meta'}->{'comparison'};

# Collect information, validate common data
foreach my $file (@FILES) {
  &read_log("$DIR/$file", \%DATA);
}

# Crunch some statistics, save results
&stats(\%DATA);

# Print all data in CSV form
&print(\%DATA);

exit();

################################################################################
#
# Stage #1: Read all the logs and organise in a
# hierarchical data structure.

sub read_log() {
  my ($file, $data) = @_;
  
  # Find or create the correct path inside hash
  # TODO: Merge with DATA initialisation above (object)
  $data = &find_create_hash($file, $data);

  # Read whole file, check common, update unique values
  open (FILE, $file) || die "Can't open $file: $!\n";
  foreach my $line (<FILE>) {
    # Common fields have to be identical
    &check_set_common($line, 'ProblemSize', "Problem size\\s+=\\s+(\\d+)", $file);
    &check_set_common($line, 'IterationCount', "Iteration count\\s+=\\s+(\\d+)", $file);
    &check_set_common($line, 'FinalEnergy', "Final Origin Energy\\s+=\\s+(\\d+\\.\\d+e[+-]\\d+)", $file);
    &check_set_common($line, 'Elements', "Total number of elements:\\s+(\\d+)", $file);

    # Run-specific are different, per file
    $data->{'threads'} = $1 if ($line =~ /Num threads: (\d+)/);
    $data->{'grind'} = $1 if ($line =~ /Grind time \(us\/z\/c\)\s+=\s+(\d+\.\d+)/);
    $data->{'fom'} = $1 if ($line =~ /^FOM\s+=\s+(\d+\.\d+)/);
    $data->{'CPUs'} = $1 if ($line =~ /(\d+\.\d+) CPUs utilized/);
    $data->{'context-switches'} = $1 if ($line =~ /(\d+)\s+context-switches/);
    $data->{'cpu-migrations'} = $1 if ($line =~ /(\d+)\s+cpu-migrations/);
    $data->{'page-faults'} = $1 if ($line =~ /(\d+)\s+page-faults/);
    $data->{'cycles'} = $1 if ($line =~ /(\d+)\s+cycles/);
    $data->{'instructions'} = $1 if ($line =~ /(\d+)\s+instructions/);
    $data->{'branches'} = $1 if ($line =~ /(\d+)\s+branches/);
    $data->{'branch-misses'} = $1 if ($line =~ /(\d+)\s+branch-misses/);
    $data->{'elapsed'} = $1 if ($line =~ /(\d+\.\d+)\s+seconds time elapsed/);
  }
  close (FILE);
}

### Guarantees all files have the same common data
sub check_set_common() {
  my ($line, $key, $regex, $file) = @_;
  return if ($line !~ /$regex/);
  my $new = $1;
  # Compare with previously stored value of same pattern
  if (defined $common->{$key} && $common->{$key} != $new) {
    die "Current value '$key = $new' on '$file' is different ".
        "than previously recorded value '".$common->{$key}."', aborting.\n";
  }
  $common->{$key} = $new;
}

### Find or create the correct path inside hash (avoid collision of data)
sub find_create_hash() {
  my ($file, $data) = @_;
  # Filenames in format Dir/Benchmark-compiler-flags-numcpus.log
  my @tags = split(/[\/-]+/, $file);
  foreach my $tag (@tags) {
    $tag =~ s/\.log$//;
    # Creates empty hash ref, to avoid undefined later
    $data->{$tag} = {} unless defined $data->{$tag};
    $data = $data->{$tag};
  }
  return $data;
}

################################################################################
#
# Stage #2: compare them N-to-M based on recursively
# descending the tree and looking for equals.

sub stats() {
  my ($data) = @_;

  my $dp = &find_first_multiple($data);

  # Find leaf categories and array of tags
  &process_categories($dp, ());

  # Make sure we have the same number of categories and data tags
  &check_meta();

  # For each category, compare with N other levels
  &compare_categories($dp, $dp, ());
}

### Recursively walk through tags, finds last and one before
sub process_categories() {
  my ($dp, @tags) = @_;

  # Recurse first, until bottom category
  my $add_cats = 0;
  my $add_data = 0;
  foreach my $cat (keys %$dp) {
    # Ignore meta
    next if ($cat eq 'meta');
    # Don't descend if data
    if (ref($dp->{$cat}) ne "HASH") {
      $add_data = 1;
      last;
    }
    $add_cats = &process_categories($dp->{$cat}, @tags, $cat);
  }

  # Add all leaf categories as data tags
  if ($add_data) {
    foreach my $dat (keys %$dp) {
      $data_tags->{$dat}++;
    }
    # We can add categories on the one-up level
    return 1;
  }

  # Add all tags as categories
  if ($add_cats) {
    foreach my $cat (keys %$dp) {
      $categories->{$cat}++;
    }
  }

  # False == don't add categories
  return 0;
}

### Make sure we have the same number of categories and data tags
sub check_meta() {
  my $count = 0;
  foreach my $dt (keys %$data_tags) {
    if ($count and $count != $data_tags->{$dt}) {
      die "Data count '$dt = $data_tags->{$dt}' not the same as '$count', ".
          "make sure all runs have the same information.\n";
    } else {
      $count = $data_tags->{$dt};
    }
  }
  $count = 0;
  foreach my $cat (keys %$categories) {
    if ($count and $count != $categories->{$cat}) {
      die "Category count '$cat = $categories->{$cat}' not the same as '$count', ".
          "make sure all runs have the same information.\n";
    } else {
      $count = $categories->{$cat};
    }
  }
}

### Search for the first tag that has multiple results (compiler, flags, opts)
sub find_first_multiple() {
  my ($data) = @_;
  # First, find the non-meta key
  my $first = '';
  foreach my $key (keys %$data) {
    next if ($key eq 'meta');
    $first = $key;
  }
  my $dp = $data->{$first};

  # Second, find the first multiple tag
  while (scalar keys %$dp == 1) {
    # only one anyway
    foreach my $key (keys %$dp) {
      $dp = $dp->{$key};
    }
  }
  return $dp;
}

### For each category, compare with N other levels
sub compare_categories() {
  my ($base, $dp, @tags) = @_;

  my $last = 0;
  foreach my $cat (sort keys %$dp) {
    # Ignore meta
    next if ($cat eq 'meta');
    # Don't descend if data
    if (ref($dp->{$cat}) ne "HASH") {
      return 1;
    }
    # This works because all categories have the same depth
    $last = &compare_categories($base, $dp->{$cat}, @tags, $cat);
  }

  # If in the last category, before data, compare
  if ($last) {
    # First, compare all last categories
    my $first = 0;
    my @first_tags = @tags;
    foreach my $cat (sort keys %$dp) {
      if (!$first) {
        push @first_tags, $cat;
        $first = 1;
      } else {
        my @cat_tags = (@tags, $cat);
        &compare($base, \@first_tags, \@cat_tags);
      }
    }
    # Second, recurse back up, compare same sub-cat to every other cat
    &compare_level($base, \@first_tags, @tags);
  }
  return 0;
}

### Compare two sub-categories of all children at the same level, recurse
sub compare_level() {
  my ($base, $first_tags, @tags) = @_;
  return unless (scalar @tags);

  # Find categories to compare
  my $dp1 = &get_hash_tag($base, $first_tags);
  my $this_tag = pop @tags;
  my $parent = &get_hash_tag($base, \@tags);
  foreach my $key (keys %$parent) {
    my @new_tags = @tags;
    push @new_tags, $key;

    # Avoid comparing the same categories
    next if ($key eq $this_tag);

    # Build new tags with all but this one category identical
    my $i = scalar @tags+1; # all tags + new key
    my $j = scalar @$first_tags-1; # up to last first tag
    for my $tag ($i..$j) {
      push @new_tags, $first_tags->[$tag];
    }

    # Compare
    my $new_dp = &get_hash_tag($base, \@new_tags);
    if ($new_dp) {
      &compare($base, $first_tags, \@new_tags);
    }
  }

  # Recurse, until no more elements left in @tags
  &compare_level($base, $first_tags, @tags);
}

### Compare two categories, creating a meta/comparison/name1-name2 tag
sub compare() {
  my ($dp, $tags1, $tags2) = @_;

  # Sort tags to make sure we don't duplicate work
  my $tag1 = join("-", @$tags1);
  my $tag2 = join("-", @$tags2);
  my $tag = '';
  if ($tags1->[-1] < $tags2->[-1]) {
    $tag = "$tag1-$tag2";
  } else {
    $tag = "$tag2-$tag1";
  }
  # Skip if comparison has already been done
  return if (defined $comparison->{$tag});

  # Find two data pointers, cache
  my $dp1 = &get_hash_tag($dp, $tags1);
  my $dp2 = &get_hash_tag($dp, $tags2);

  # Compare each data (they have been checked to exist on both)
  foreach my $key (keys %$dp1) {
    if (!$dp1->{$key}) {
      $comparison->{$tag}->{$key} = $dp2->{$key};
    } else {
      $comparison->{$tag}->{$key} = $dp2->{$key} / $dp1->{$key};
    }
  }
}

### Navigate down the tags list and return a pointer to the hash reference
sub get_hash_tag() {
  my ($dp, $tags) = @_;
  foreach my $tag (@$tags) {
    $dp = $dp->{$tag};
  }
  return $dp;
}

### Compare two arrays, return true if identical up to element N
sub compare_arrays() {
  my ($array1, $array2, $depth) = @_;
  for my $i (0..$depth-1) {
    return 0 if ($array1->[$i] != $array2->[$i]);
  }
  return 1;
}

################################################################################
#
# Stage #3: Print the results in a CSV format

sub print() {
  my ($data) = @_;

  # For now, let's just dump the comparison
  my $first = 1;
  foreach my $comp (sort keys %$comparison) {
    # Header
    if ($first) {
      print "Comparison,";
      foreach my $key (sort keys %{$comparison->{$comp}}) {
        print "$key,";
      }
      print "\n";
      $first = 0;
    }
    # Comparison
    print "$comp,";
    foreach my $key (sort keys %{$comparison->{$comp}}) {
      print $comparison->{$comp}->{$key}.",";
    }
    print "\n";
  }
}
