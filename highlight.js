
function initNote(){
    //do nothing
}

// Helper function to escape special characters in strings for use in regular expressions
function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Function to create a regex pattern for a given word count
function createPattern(words, count) {
  const wordSegment = words.slice(0, count).join(' ');
  return new RegExp(escapeRegExp(wordSegment), 'gi');
}

// Function to find and highlight matches
function highlightMatches(pattern, className) {
  let matches = [];
  let match;
  while ((match = pattern.exec(haystack)) !== null) {
    matches.push(match);
  }

  if (matches.length === 1) {
    haystack = haystack.replace(matches[0][0], `<span class="${className}">${matches[0][0]}</span>`);
  }
}

window.addEventListener('load', function() {
    // Check if URL contains the highlight parameter
    if (window.location.hash) {
      console.log("***textparam detected=", window.location.hash)
        var textToHighlight = decodeURIComponent(window.location.hash.replace(/\+/g, ' '));
        if (textToHighlight.startsWith("#")) {
          textToHighlight = textToHighlight.substring(1);
        }
        //highlightText(textToHighlight);

        console.log("***sb1", textToHighlight);
        
        // Create a <style> element
        const style = document.createElement('style');

        // Set the CSS content
        style.textContent = `
          .gradient-highlight {
            background: linear-gradient(to right, lightblue, rgba(173, 216, 230, 0));
          }
          .gradient-highlight-backward {
            background: linear-gradient(to left, lightblue, rgba(173, 216, 230, 0));
          }
          SUP {
            user-select: none;
          }
          SUP > A {
            text-decoration: none; /* remove underline */
            color: blue; 
          }
        `;

        // Append the <style> element to the <head>
        document.head.appendChild(style);

        const needle = textToHighlight.trim();
        let haystack = document.body.innerHTML;

        // Helper function to escape special characters in strings for use in regular expressions
        function escapeRegExp(string) {
          return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        }

        // Function to create a regex pattern for a given word count
        function createPattern(words, count) {
          const wordSegment = words.slice(0, count).join(' ');
          return new RegExp(escapeRegExp(wordSegment), 'gi');
        }

        // Function to find and highlight matches
        function highlightMatches(pattern, className) {
          let matches = [];
          let match;
          console.log("Looking for match...", pattern);
          while ((match = pattern.exec(haystack)) !== null) {
            matches.push(match);
          }

          if (matches.length === 1) {
            console.log("***found match!")
            haystack = haystack.replace(matches[0][0], `<span class="${className}">${matches[0][0]}</span>`);
          }
        }

        // Split the needle into words
        const words = needle.split(' ');

        // Try to highlight the first and last 5 words
        let firstPattern = createPattern(words, 5);
        let lastPattern = createPattern(words.slice(-5), 5);

        highlightMatches(firstPattern, 'gradient-highlight');
        highlightMatches(lastPattern, 'gradient-highlight-backward');

        // If no matches found for first and last 5 words, try with 3 words
        if (!haystack.includes('gradient-highlight') && !haystack.includes('gradient-highlight-backward')) {
          firstPattern = createPattern(words, 3);
          lastPattern = createPattern(words.slice(-3), 3);

          highlightMatches(firstPattern, 'gradient-highlight');
          highlightMatches(lastPattern, 'gradient-highlight-backward');
        }

        // Update the content element with the highlighted text
        document.body.innerHTML = haystack;

        var targetSpan = document.querySelector('span.gradient-highlight-backward');
    
        // Check if the element exists to avoid errors
        if (targetSpan) {
            var elementRect = targetSpan.getBoundingClientRect();
            var absoluteElementTop = elementRect.top + window.pageYOffset;
            var middle = absoluteElementTop - (window.innerHeight / 2) + (elementRect.height / 2);
  
            // Scroll the element into view
            //targetSpan.scrollIntoView({ behavior: 'smooth', block: 'start' });
            window.scrollTo({
                top: middle,
                behavior: 'smooth'
            });
        }
        else {
          targetSpan = document.querySelector('span.gradient-highlight');
          if (targetSpan) {
            var elementRect = targetSpan.getBoundingClientRect();
            var absoluteElementTop = elementRect.top + window.pageYOffset;
            var middle = absoluteElementTop - (window.innerHeight / 2) + (elementRect.height / 2);
    
            //targetSpan.scrollIntoView({ behavior: 'smooth', block: 'start' });
            window.scrollTo({
                top: middle,
                behavior: 'smooth'
            });
          }

        }

    }


});

