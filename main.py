from config.config import settings
from agents.researcher.graph import researcher
from IPython.display import Markdown
from collections import deque

def show_analysts(analysts):
    if analysts:
        for analyst in analysts:
            print(f"Name: {analyst.name}")
            print(f"Affiliation: {analyst.affiliation}")
            print(f"Role: {analyst.role}")
            print(f"Description: {analyst.description}")
            print("-" * 50)
    else:
        print("No analysts found.")

if __name__ == "__main__":
    topic = input(">>> Enter a topic: ")
    print(topic)
    
    max_analysts = 3 
    thread = {"configurable": {"thread_id": "1"}}
    
    # Run the graph until the first interruption
    for event in researcher.stream({"topic":topic,
                            "max_analysts":max_analysts}, 
                            thread, 
                            stream_mode="values"):
        
        analysts = event.get('analysts', '')
        show_analysts(analysts)
    
    while True:
        human_analyst_feedback = input(">>> Do you want to give feedback on the analysts? (yes/no): ").strip().lower()
        if human_analyst_feedback == 'yes':
            feedback = input(">>> Enter your feedback: ")
            researcher.update_state(thread, {"human_analyst_feedback": feedback}, as_node="human_feedback")
            
            generator_analysts = researcher.stream(None, thread, stream_mode="values")
            last_value = deque(generator_analysts, maxlen=1).pop()
            analysts = last_value.get('analysts', '')
            show_analysts(analysts)
        elif human_analyst_feedback == 'no':
            researcher.update_state(thread, {"human_analyst_feedback": None}, as_node="human_feedback")
            print("*"*20, "End of feedback.", "*"*20)
            break
        else:
            print(">>> Please enter 'yes' or 'no'.")
    
    print("*"*20, "Start of interviews and write report.", "*"*20)
    for event in researcher.stream(None, thread, stream_mode="updates"):
        node_name = next(iter(event.keys()))
        print("Done: ", node_name)
        
    final_state = researcher.get_state(thread)
    report = final_state.values.get('final_report')
    report_fully = Markdown(report)
    with open("result.md", "w", encoding="utf-8") as f:
        f.write(report)