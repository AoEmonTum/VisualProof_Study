
<style>
.study-shell {
    max-width: 1120px;
    margin: 0 auto;
    padding: 8px 20px 36px;
    color: #1f2937;
}

.study-hero {
    padding: 28px 30px;
    border-radius: 24px;
    background: linear-gradient(135deg, #f7fbff 0%, #eef4ff 100%);
    border: 1px solid #dce7f5;
    box-shadow: 0 16px 36px rgba(15, 23, 42, 0.06);
}

.study-kicker {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #3461d9;
}

.study-title {
    margin: 10px 0 10px;
    font-size: 34px;
    line-height: 1.1;
    font-weight: 750;
    color: #10213a;
}

.study-lead {
    margin: 0;
    font-size: 17px;
    line-height: 1.8;
    color: #354255;
    max-width: 72ch;
}

.study-example {
    margin-top: 18px;
    padding: 14px 16px;
    border-radius: 20px;
    background: white;
    border: 1px solid #dce7f5;
}
.study-note {
    margin-top: 18px;
    padding: 16px 18px;
    border-radius: 16px;
    background: #f5f8fc;
    border-left: 4px solid #3461d9;
    font-size: 15px;
    line-height: 1.7;
    color: #344457;
}

.study-example img {
    width: 100%;
    max-height: 240px;
    object-fit: contain;
    display: block;
    margin-top: 16px;
}
</style>

<div class="study-shell">
  <div class="study-hero">
    <div class="study-kicker">Introduction</div>
    <div class="study-title">What exactly are graphs?</div>
    <p class="study-lead">
      To understand what type of graphs we are talking about in this study, we will start with an example: Lets imagine we want to model a social network. We would want the network to represent people and friendships between people. For that we can depict people in a space and link them with lines if they are friends.
    </p>

<div class="study-example">
      <h3 style="margin:0;font-size:18px;color:#10213a;">Our social network example</h3>
      <img src="visual-proof-study-pilot-1/assets/socialNetwork/1.png" alt="Social network graph">
      <p style="margin:12px 0 0;font-size:15px;line-height:1.75;color:#445469;">
        Here we can see a group of seven people visualized on a white plane and positioned randomly. Their friendships are represented by lines connecting them. It's easy to see that Lara and Ben are friends as well as that Ida and Mia are not. But what about other properties of this group of people? Is there a person that connects these people, that without them, the group would be split into two? This is a much harder question to answer by just looking at the graph. The freedom to position the people in the space is a challenge, as different arrangements can make certain properties of the group easier or harder to recognize.
      </p>
    </div>

<div class="study-example">
      <h3 style="margin:0;font-size:18px;color:#10213a;">The same group arranged differently</h3>
      <img src="visual-proof-study-pilot-1/assets/socialNetwork/2.png" alt="Organized social network graph">
      <p style="margin:12px 0 0;font-size:15px;line-height:1.75;color:#445469;">
        By arranging the same people differently, it can become easier to answer questions about certain properties of the group. For example, it is now easier to see that without Zoë, the group would be split into two. So there is a person that connects the two groups of friends.
      </p>
    </div>
<div class="study-example">
      <h3 style="margin:0;font-size:18px;color:#10213a;">The graphs in computer science</h3>
      <img src="visual-proof-study-pilot-1/assets/socialNetwork/3.png" alt="Abstract social network graph">
      <p style="margin:12px 0 0;font-size:15px;line-height:1.75;color:#445469;">
        If we now strip away the visual details such as the names of the people, and we depict a person as a node, we can see that the graph is now an abstract representation of the social network. This is how graphs are used in computer science: they are abstract representations of relationships between objects. The objects are represented by nodes and the relationships by links.
      </p>
    </div>
<div class="study-example">
      <h3 style="margin:0;font-size:18px;color:#10213a;">The study</h3>
      <p style="margin:12px 0 0;font-size:15px;line-height:1.75;color:#445469;">
        In this study we will be focusing on three properties of graphs: bipartiteness, Hamiltonian cycles, and cut vertices. We will introduce and explain each property and then you will be asked to answer questions about graphs that either have or do not have the property. 
      </p>
    </div>
<div class="study-note">
        Let's start with the first property! Click on "Next" to continue.
    </div>

  </div>
</div>
