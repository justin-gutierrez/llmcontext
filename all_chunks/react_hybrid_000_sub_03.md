# react_hybrid_000_sub_03

**Metadata:** {'strategy': 'hybrid', 'header_level': 1, 'line_count': 7, 'document_id': 'react', 'sub_chunk_index': 3, 'total_sub_chunks': 4}

**Tokens:** 3000-3309

---

 of the buttons. Finally, change MyButton to read the props you have passed from its parent component: function MyButton({ count, onClick }) { return ( &lt;button onClick={onClick}&gt; Clicked {count} times &lt;/button&gt; );} When you click the button, the onClick handler fires. Each button’s onClick prop was set to the handleClick function inside MyApp, so the code inside of it runs. That code calls setCount(count + 1), increment

ing the count state variable. The new count value is passed as a prop to each button, so they all show the new value. This is called “lifting state up”. By moving state up, you’ve shared it between components. App.jsApp.js ResetForkimport { useState } from &#x27;react&#x27;; export default function MyApp() { const [count, setCount] = useState(0); function handleClick() { setCount(count + 1); } return ( &lt;div&gt; &lt;h1&gt;Counters that update together&lt;/h1&gt; &lt;MyButton count={count} onClick={handleClick} /&gt; &lt;MyButton count={count} onClick={handleClick} /&gt; &lt;/div&gt; ); } function MyButton({ count, onClick }) { return ( &lt;button onClick={onClick}&gt; Clicked {count} times &lt;/button&gt; ); } Show more Next Steps By now, you know the basics of how to write React code! Check out the Tutorial to put them into practice and build your first mini-app with React.NextTutorial: Tic-Tac-ToeCopyright © Meta Platforms, Incno uwu plzuwu?Logo by@sawaratsuki1004Learn ReactQuick StartInstallationDescribing the UIAdding InteractivityManaging StateEscape HatchesAPI ReferenceReact APIsReact DOM APIsCommunityCode of ConductMeet the TeamDocs ContributorsAcknowledgementsMoreBlogReact NativePrivacyTerms