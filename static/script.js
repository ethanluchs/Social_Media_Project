// Questionnaire page functionality
if (document.querySelector('form')) {
    // Character counter for textareas
    document.querySelectorAll('textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            const counter = this.nextElementSibling;
            counter.textContent = `${this.value.length}/450 characters`;
        });
    });

    // Form submission handler
    document.querySelector('form').addEventListener('submit', async function(e) {
        e.preventDefault();  // Prevent default form submission
        
        // Create an object with the form data
        const formData = {
            social_connection: document.querySelector('textarea[name="social_connection"]').value,
            self_esteem: document.querySelector('textarea[name="self_esteem"]').value,
            strategies: document.querySelector('textarea[name="strategies"]').value,
            growth: document.querySelector('textarea[name="growth"]').value
        };

        // Create the formatted text content for download
        const questions = {
            social_connection: "How does Instagram help or hinder your relationships with friends, family, or your community?",
            self_esteem: "In what ways does Instagram impact your self-esteem or lead to comparisons with others?",
            strategies: "What strategies do you use to manage your time, set boundaries, or limit overwhelming content on Instagram?",
            growth: "How does the content you follow or engage with on Instagram inspire or motivate your personal or professional growth?"
        };

        let textContent = "Social Media Habits Questionnaire Responses\n";
        textContent += "Date: " + new Date().toLocaleString() + "\n\n";

        // Add each question and response to the text content
        for (const [key, response] of Object.entries(formData)) {
            textContent += "Question: " + questions[key] + "\n";
            textContent += "Response: " + response + "\n\n";
        }

        // Create and trigger download of the text file
        const blob = new Blob([textContent], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'questionnaire_responses.txt';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        try {
            const response = await fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            if(result.success) {
                alert('Responses submitted successfully!');
                // Could redirect to an insights page here:
                // like window.location.href = '/insights';
            }
        } catch (error) {
            console.error('Error:', error);
            alert('There was an error submitting your responses.');
        }
    });
}

// Insights page functionality
if (document.getElementById('analyzeButton')) {
    console.log('Insights page detected');  // Debug log
    
    // Update file name display when files are selected
    document.querySelectorAll('.file-input').forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0] ? this.files[0].name : 'No file chosen';
            this.nextElementSibling.textContent = fileName;
        });
    });

    // Handle analyze button click
    document.getElementById('analyzeButton').addEventListener('click', async function() {
        try {
            // Show loading state
            this.disabled = true;
            this.textContent = 'Analyzing...';

            // Create FormData object
            const formData = new FormData();
            
            // Add files to FormData
            const fileInputs = {
                questionnaireFile: document.getElementById('questionnaireFile'),
                accountInfoFile: document.getElementById('accountInfoFile'),
                activityFile: document.getElementById('activityFile'),
                connectionsFile: document.getElementById('connectionsFile'),
                contentFile: document.getElementById('contentFile')
            };

            for (const [key, input] of Object.entries(fileInputs)) {
                if (input.files[0]) {
                    console.log(`Adding file: ${key} - ${input.files[0].name}`);  // Debug log
                    formData.append(key, input.files[0]);
                }
            }

            console.log('FormData created, sending to server...');  // Debug log

            // Send files for analysis
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                // Update insight sections with the results
                const insights = result.insights;
                
                // Update each insight section
                document.querySelector('[data-section="social_connection"] .insight-text')
                    .value = insights.social_connection;
                document.querySelector('[data-section="goal_focus"] .insight-text')
                    .value = insights.goal_focus;
                document.querySelector('[data-section="self_worth"] .insight-text')
                    .value = insights.self_worth;
                document.querySelector('[data-section="moderation"] .insight-text')
                    .value = insights.moderation;
                    
                alert('Analysis completed successfully!');
            } else {
                alert('Error analyzing data: ' + result.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('There was an error analyzing your data.');
        } finally {
            // Reset button state
            this.disabled = false;
            this.textContent = 'Analyze Data';
        }
    });
}