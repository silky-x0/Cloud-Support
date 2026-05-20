import asyncio
import uuid
import sys
from agents.orchestrator import create_conversation, chat

async def main():
    print("Welcome to CloudDash Support CLI!")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    customer_id = input("Enter Customer ID (optional): ").strip()
    state = create_conversation(customer_id)
    conv_id = state.conversation_id
    
    print(f"\nStarted conversation: {conv_id}")
    print("-" * 40)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            
            if not user_input:
                continue
                
            response = await chat(conv_id, user_input)
            
            print(f"\nAgent ({response.agent}): {response.content}")
            
            if response.citations:
                print("\nCitations:")
                for cit in response.citations:
                    print(f"- [{cit.kb_id}] {cit.title} (Score: {cit.score})")
                    
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            
    print("\nThank you for using CloudDash Support. Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())
