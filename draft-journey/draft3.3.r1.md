Then I will give you my all mental model again. So can you help me check all arc now that in my direction or not:

1. Scap (SRAM + Capacitor)

The atom unit of all model.

- Componet
  - Capacitor + Cascode to holding weight
  - 1 bit SRAM for sign
  - 8 bit SRAM for rechage (Control the leakage to less as we want, can use to be nature weight decay)
  - 16 bit SRAM for contribution (keep as moemtum 0.75 old + 0.25 new)
  - N\*M bit SRAM for path

- Addition
  - contributeion keep by contribution-base (a dot w)
  - input as a update_signal use to be learning rate or update amount. The concept it, when this signal == 1, the Scap's weight capacitor will be update on it distribution. Which now distribution was keeping by Binary, so we use PWM pulse to update it amout. (Update signal is long 1 areas, braodcast to all scap. Then the scap recieve it signal and update its weight only when distibution pulse said. Making simple circuit)

2. Ganglion

The unit that wiring scap togather to copy 1 axon machanism. Using the 2-3-3-2 complexity to act like a multi-synapse activity. (the distace to next dendrive, the dense of synapse, the amout of hormone to send, etc. Act to represent by 2-3-3-2 model)

- Component
  - 2-3-3-2 scap
  - 2 input capacitor
  - 2 output capacitor
  - 3 + 3 activate fuction for only middle layer. (last layer not use to keep the range)

- ALU
  - the ALU will be hardwire for 2-3-3-2, input as 2 input capacitor, then charging to 2 output capacitor, by directly using the weight from scap inside to op-amp computation
  - Because we use 2-3-3-2 neural, so we use 2x3 + 3x3 + 3x2 scap weight, and 3 + 3 + 2 for bias. Using 29 scaps. And 3 + 3 activate function
  - While otuput capacitor was charging, the ALU will use another 29 capacitor to measure each scap distribution, use another 3+3+2 to measure the neural weight. Change analog value to SRAM. Then write back to each scap how it participate this distribution

3. Column

Because Ganglion is acting like only one axon cell. The column will be assembly of real network.

Because ALU size is limit. So we using floating local capacitor to keep temporary state of each network output. (The first Ganglion1 comput and keep output capacitor to c1 and c2. Then this c1 and c2 will be input of next Ganglion1 and Ganglion2, produce c3, c4, c5, c6, etc. So we can chain the dimention of model. (Defual ganglion was destroy dimention itself to project real synapse machanism))

So thes Column will have translate ALU instead. And this translate will use 1 scap / 1 wires

- Component
  - 2:2 Translate, using 2\*2 scap
  - 2:4 Translate, using 2\*4 scap
  - ...

- ALU
  - 2:2 Translate
  - 2:4 Translate
  - 4:4 Translate
  - 4:5 Translate
  - ...

So now we we get

- Ganglion: it's 2 input to 2 output
- Column: it's n input to m input

4. Limbic

It's like next level of column again. It's duty is increase the model dimesion. But this Limbic part will be more special. We have many trick such as:

    1.0. Column1 (4:4)
    - recieve 4 initial input then predict 4 output

    2.1. Column2 (4:4)
    - recieve 4 from Column1 then predict 4 output

    2.1. Column3 (8:4)
    - recieve 4 from Column1 then predict 4 output
    - recieve 4 from Column2 then predict 4 output
    - (4:4 from Column1 to Column3 And 4:4 from Column2 to Column3, is seperate. It's 2 4:4, not a 4:8)

The ALU may use the same of column. I didn't hink about complexity heirachy yet

5. Limbic Loop

It's just a recurrent loop of hippo campus and prefontal cortext like we do

- Component
  - Input quality down grade module (prevent hippo campus overfit or remember only specific thing)
  - CNC (Connect prefontal and hippo campus)

---

My next level ideas to make model come true

1. The Variant or Vanish Improving

Because of now we're both in analog and in dynamic learning. The variant is too high.

The first initial is able to broke all model before it learns something.

So I have an Ideas to use special H(x), H(x) is an output of each neural

- From normal (Gradient descend): H(x) = prediction
- My New Ideas (original distribute base): H(x) = prediction + x

This will make x chain for all neural, making x meaning not vanish throught the layer

And then we will make the prediction variant is making predict < x

Because of now, we don't have initial theory yet, I will use He or Xavier to explain it first.

At the core of intial theory, we just want to make every layer have same variant. Making all model have same range of swing value stable, not explode or vanish.

But when we go to use H(x) = prediction + x

Now our variant of each layer output is var(prediction) + var(X). Which a var(X) will make overall variant increase and increase

But we can solve it by nomalize all data to make reduce varaint = var(prediciton') again. So all layer will have same varaint

I think this is helping us so much to fight with analog noise and new model convergence. But I didn'thave stable model yet, how can we normalize it to circuit.

2. The attribute base problem, Improving

As you see our Delta w ∝ a·w, this problem can easily solve in modern model by just let relu solving it. But we haven't that attribute. Our capacitor have limit range

So my thought now is local-aware algorithm. Now our backpropagation model is who have much distribute, get much update. But the problem is we have a limit of its weight, and it doesn't have some trigger yet when some weight is hiting capacity limit. So if we can find the way to measure how each neural capacitor left, then building normalize function to make every epoch, the update capacity should be a same. That time we will defitenitely solve this vanish problem. Making model convergence faster.

But to build this formular, I have to think myself first. What should we copmute overall update capacitor should be. Because if all batch have to update the same capacitor, it mean the important batch may get same priority as trash bath too. But I think we're nearing the solution.
