1. The Aiming section says "Making encryption algorithm inspired by real-world biology cell." Is encryption literal here (cryptographic primitive) or are you using it to mean compressed/encoded representation — i.e. the brain encodes meaning densely in capacitor states? These are very different projects and I want to write the right one.
   Yeah, encryption there mean about "my algorithm that can compress all weight data that normally will be save in Storage or RAM, live in only cpu"

1. What's the target task to measure success on? MNIST? A custom sequence-prediction task? Some abstract "remembers a pattern" benchmark? Without this, "model complexity" and "less computation" have no units.
   I don't sure about it yet. But may be compare between in-model. Not just external model to compare yet, until final model was done. I think The convergence type or pattern recognize will be my metric now, due to my new backpropagation formular.

1. For the Python simulation: do you want behavioral (numpy/torch math that mirrors the architecture but skips circuit physics) or circuit-faithful (something closer to SPICE-style with op-amp non-idealities, capacitor leakage, charge timing)? Or both, in stages?
   I want ideal model fisrt, then those robust attribute will be secondary.

1. You say weights along the active path get reduced by a constant `c`, with the sign coming from a per-scap sign SRAM and direction from tri-state feedback (−, 0, +). I think I get the spirit (let e^t capacitor dynamics turn constant pulses into exponential, self-stabilizing updates) but I'm not sure how the credit assignment happens. In standard backprop, layer L gets gradient = output*error × W*{L+1} × ... How does your scheme tell scap #3 in layer 2 that it specifically contributed to the error, versus scap #1? Is it just "every scap on the active path moves the same direction, and noise + the e^t curve sorts out who deserved it over many samples"? If so, that's a strong claim worth stating as the central hypothesis to test.
   Yeah, good catch. This is my problem too. If using distribute shared backpopagation, all neural have to know each other. This c eqaul penalty backpopagation is the old trick of ml. It's the trick before even real backpopagation born. Eventually this c-equal value with negative/possitive update will be able to push model to convergence some where. But it's so sensitive. And This is my main research too. How we will build the update weight formular for it inspired by real biology cell.

1. When you say `L1 → L2 → L1 → L3 → L1 → L4`, is L1 the same physical NCN being called three times with different inputs/contexts, or is it a logical pattern (three different L1-typed NCNs)? If it's the same physical one, how does it know it's now "between L2 and L3" vs "between L3 and L4"? Is the context encoded in which specialist drove it, or is there an explicit context input?
   L1 is the same for all. Such we set L1 with 4 input and 6 output. The L2 and L3 just make same 6 input and 4 output to connect it. The main goal is just reuse the neural, increase model complexity by just using the same amout capactor or SRAM.

1. What is "distance" measuring physically? Distance in 1D address space between sender and receiver scap? And what does multiplying `output × distance` actually do for the computation — is `distance` acting like a learned weight that's stored as position instead of capacitor charge? If yes, that's elegant; I want to make sure I describe it right. 7
   This is the optional ideas now too, Because more step above still not stable. This topic talk about we will use binary signal to call out in global chanel, then calling the child that nearing it. Every 1D data will be compress in that binary. And we will use hardwired op-amp multiplier like to apply it scale. (the first ideas now, required so much thing to optimize)

1. Does the position itself update during learning, or only at init?
   Good catch again, now the backpapagation will apply both capacitor weight and it 1D position. Making those neural can allocate more faster. We just reduce/incrase that SRAM position by simeple now (first ideas)

1. Low grade input" to hippocampus — concretely, is this downsampled? Quantized? Routed through fewer scaps? I read it as "lossy compression so hippocampus can't cheat by reading raw input and bypassing the prefrontal loop." Correct?
   I have no ideas now what is best. But my ideas now is reducing it feature neural. Such as real input will have 20 feature. So we use simple NCN or hardwire circuit to reduce it to 5 feature, reduce it qaulity, while able to keep catagory-like level pattern.

1. The CNS between prefrontal and hippocampus — is it itself a trainable NCN group, or fixed wiring?
   Still have no ideas yet, I don't sure now that if I train CNS too, it will be broke due to sensitivity or not. have to experiment. But I think I may let everything learn togather, just this part may have less learning rate than other.

On routes 10. 4-bit L1 × 4-bit L2 = 256 NCNs total in the first prototype. Is that the target scale for the whole brain in draft2, or just one cortex region? Knowing the size sets everything else.

Yeah, target is to scale to whole brain. But I don't sure yet how much is brain require now to built simple intelligence. (don't sure that how much 256 NCN can do, making don't sure yet should overengineer it at first or not)

Two unfinished sections 11. STM is marked Prototype — include in draft2 as a stub with "future work" notes, or leave out entirely?
This is the ideas that didn't reflect yet. You can leave it blank now.

12. The "cell fire" section ends mid-sentence ("I will use"). Do you want to leave it as an open research thread, or do you have an STDP variant in mind I should help formalize?
    This too, The cell fire mechanism is too hard and too sensitive to do. I have no good ideas yet.
