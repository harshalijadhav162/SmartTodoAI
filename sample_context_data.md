# Sample Context Data for Testing SmartTodoAI

## WhatsApp Messages

### High Priority Context
```
Content: "Urgent: Client meeting tomorrow at 2 PM. Need presentation ready by noon. This is critical for the quarterly review."
Source Type: whatsapp
Source Title: Work Group Chat
```

### Medium Priority Context
```
Content: "Team lunch on Friday at 1 PM. Please confirm attendance by Thursday."
Source Type: whatsapp
Source Title: Team Chat
```

### Low Priority Context
```
Content: "Weather looks great for the weekend. Anyone up for a hike?"
Source Type: whatsapp
Source Title: Friends Group
```

## Email Context

### Work Email
```
Content: "Subject: Project Deadline Extension

Hi team,

The client has requested an extension for the website redesign project. New deadline is August 25th. Please update your schedules accordingly.

Best regards,
Project Manager"
Source Type: email
Source Title: Project Update Email
```

### Personal Email
```
Content: "Subject: Newsletter Subscription

Thank you for subscribing to our weekly newsletter. You'll receive updates every Monday.

Regards,
Newsletter Team"
Source Type: email
Source Title: Newsletter Confirmation
```

## Notes Context

### Meeting Notes
```
Content: "Weekly Team Meeting Notes:
- Q3 goals review
- New project kickoff next week
- Budget approval pending
- Team building event planning
- Performance review cycle starts next month"
Source Type: notes
Source Title: Weekly Team Meeting
```

### Personal Notes
```
Content: "Personal To-Do:
- Call dentist for appointment
- Buy birthday gift for mom
- Schedule car maintenance
- Plan weekend trip
- Update resume"
Source Type: notes
Source Title: Personal Tasks
```

## Calendar Context

### Work Calendar
```
Content: "Calendar Entry: Client Presentation
Date: August 15, 2025
Time: 2:00 PM - 3:30 PM
Location: Conference Room A
Description: Quarterly review presentation with major client. Need to prepare slides and demo materials."
Source Type: calendar
Source Title: Client Presentation
```

### Personal Calendar
```
Content: "Calendar Entry: Doctor Appointment
Date: August 12, 2025
Time: 10:00 AM - 11:00 AM
Location: Medical Center
Description: Annual checkup with Dr. Smith"
Source Type: calendar
Source Title: Doctor Appointment
```

## How to Use This Sample Data

1. **Add Context**: Use the "📝 Add Context" button in the application
2. **Select Source Type**: Choose the appropriate source type (whatsapp, email, notes, calendar)
3. **Add Source Title**: Provide a descriptive title
4. **Paste Content**: Copy and paste the content from above
5. **Submit**: The AI will process and analyze the context

## Expected AI Insights

### High Priority Context
- **Sentiment**: Neutral to Positive
- **Keywords**: urgent, client, meeting, presentation, critical, quarterly
- **Priority Score**: High (0.8-0.9)
- **Action Items**: Prepare presentation, schedule meeting

### Medium Priority Context
- **Sentiment**: Positive
- **Keywords**: team, lunch, confirm, attendance
- **Priority Score**: Medium (0.5-0.6)
- **Action Items**: Confirm attendance

### Low Priority Context
- **Sentiment**: Positive
- **Keywords**: weather, weekend, hike
- **Priority Score**: Low (0.3-0.4)
- **Action Items**: Plan weekend activity

## Testing AI Task Suggestions

After adding context, try creating tasks with these titles:

1. **"Prepare client presentation"** - Should get high priority and work category
2. **"Buy lunch supplies"** - Should get medium priority and personal category
3. **"Plan weekend activities"** - Should get low priority and personal category
4. **"Schedule team meeting"** - Should get medium priority and work category

The AI will use the context to:
- Calculate appropriate priority scores
- Suggest relevant categories and tags
- Recommend realistic deadlines
- Enhance task descriptions with context-aware details
