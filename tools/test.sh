#!/usr/bin/env bash
#
# Build and test the site content
#
# Requirement: html-proofer, jekyll
#
# Usage: See help information

set -eu

SITE_DIR="_site"

_config="_config.yml"

_baseurl=""

# Temporary file for htmlproofer output
HTMLPROOFER_OUTPUT=$(mktemp)
trap "rm -f $HTMLPROOFER_OUTPUT" EXIT

# Check if gems are installed and install if needed
check_and_install_gems() {
  if ! bundle check > /dev/null 2>&1; then
    echo "> Required gems not found. Running 'bundle install'..."
    bundle install
  fi
}

help() {
  echo "Build and test the site content"
  echo
  echo "Usage:"
  echo
  echo "   bash $0 [options]"
  echo
  echo "Options:"
  echo '     -c, --config   "<config_a[,config_b[...]]>"    Specify config file(s)'
  echo "     -h, --help               Print this information."
}

read_baseurl() {
  if [[ $_config == *","* ]]; then
    # multiple config
    IFS=","
    read -ra config_array <<<"$_config"

    # reverse loop the config files
    for ((i = ${#config_array[@]} - 1; i >= 0; i--)); do
      _tmp_baseurl="$(grep '^baseurl:' "${config_array[i]}" | sed "s/.*: *//;s/['\"]//g;s/#.*//")"

      if [[ -n $_tmp_baseurl ]]; then
        _baseurl="$_tmp_baseurl"
        break
      fi
    done

  else
    # single config
    _baseurl="$(grep '^baseurl:' "$_config" | sed "s/.*: *//;s/['\"]//g;s/#.*//")"
  fi
}

# Parse htmlproofer output and create a table of broken links
parse_and_report_htmlproofer_errors() {
  local output_file="$1"
  
  echo
  echo "╭─ Link Validation Failures ─────────────────────────────────────────╮"
  
  local -a data=()
  
  # Parse htmlproofer output: extract lines matching "* At <file>:<line>:" 
  # followed by the indented issue description
  local prev_location=""
  local prev_issue=""
  
  while IFS= read -r line; do
    # Match "* At <file>:<line>:" pattern - this is a failure location
    if [[ $line =~ ^\*\ At\ ([^:]+):([0-9]+): ]]; then
      # If we had a previous entry, store it
      if [[ -n $prev_location ]]; then
        data+=("${prev_location}|${prev_issue}")
      fi
      # Start new entry
      prev_location="${BASH_REMATCH[1]##*/_site/}:${BASH_REMATCH[2]}"
      prev_issue=""
    # Match indented content (the issue description)
    elif [[ $line =~ ^[[:space:]]+(.+)$ && -n $prev_location ]]; then
      if [[ -z $prev_issue ]]; then
        prev_issue="${BASH_REMATCH[1]}"
      fi
    fi
  done < "$output_file"
  
  # Don't forget the last entry
  if [[ -n $prev_location ]]; then
    data+=("${prev_location}|${prev_issue}")
  fi
  
  # Print table header
  printf "│ %-35s │ %-30s │\n" "Location" "Issue"
  echo "├─────────────────────────────────────┼────────────────────────────────┤"
  
  # Print table rows
  for entry in "${data[@]}"; do
    local location="${entry%%|*}"
    local issue="${entry##*|}"
    # Truncate long strings for display
    location="${location:0:35}"
    issue="${issue:0:30}"
    printf "│ %-35s │ %-30s │\n" "$location" "$issue"
  done
  
  echo "╰─────────────────────────────────────┴────────────────────────────────╯"
  echo
  echo "Total failures: ${#data[@]}"
  echo
}

main() {
  # clean up
  if [[ -d $SITE_DIR ]]; then
    rm -rf "$SITE_DIR"
  fi

  read_baseurl

  # build
  echo "> Building site..."
  JEKYLL_ENV=production bundle exec jekyll b \
    -d "$SITE_DIR$_baseurl" -c "$_config" > /dev/null 2>&1
  echo "  ✓ Build complete"

  # test
  echo "> Running htmlproofer..."
  if bundle exec htmlproofer "$SITE_DIR" \
    --disable-external \
    --ignore-urls "/^http:\/\/127.0.0.1/,/^http:\/\/0.0.0.0/,/^http:\/\/localhost/,/^https:\/\/pilakkat.mywire.org\/(blog|cv)\//" \
    > "$HTMLPROOFER_OUTPUT" 2>&1; then
    echo "  ✓ All links validated"
  else
    # htmlproofer failed, parse and display results
    echo "  ✗ Link validation failed"
    parse_and_report_htmlproofer_errors "$HTMLPROOFER_OUTPUT"
    echo "Full htmlproofer output:"
    echo "─────────────────────────────────────────────────────────────"
    cat "$HTMLPROOFER_OUTPUT"
    echo "─────────────────────────────────────────────────────────────"
    return 1
  fi
}

while (($#)); do
  opt="$1"
  case $opt in
  -c | --config)
    _config="$2"
    shift
    shift
    ;;
  -h | --help)
    help
    exit 0
    ;;
  *)
    # unknown option
    help
    exit 1
    ;;
  esac
done

check_and_install_gems

main
