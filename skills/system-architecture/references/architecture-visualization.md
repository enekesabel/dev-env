# Visualizing the architecture

Draw from the [architecture document](architecture-document.md), not from fresh exploration.
Use the environment's own visualization capability (canvas, artifact, or diagram skill).

- **One picture.** The containers sit inside the system boundary, with the Context's actors
  and external systems around it.
- **Edges reach the containers.** Edges from actors and external systems connect to the
  container they interact with, not to the system boundary.
- **Grouping follows the Physical lens:** group and color containers that share a deployment
  node in the environment shown. Let the viewer switch environments; show the development
  environment by default.
- **Distinct kinds:** actors, containers, and external systems look different from each other.
- **One arrow per connection,** pointing from the initiator and labeled with its flows.
- **Flows read in screen direction.** Next to its connection, each flow's arrow points the way
  that data moves along the line as drawn.
- **The environment shown decides** the grouping by deployment node, how each container and
  external system is realized, and what counts as inferred: an element is inferred when its
  own evidence or its entry for that environment is inferred.
- **Descriptions are visible:** each actor's goal, each external system's capability, and
  each container's responsibility.
- **Inferred versus verified:** shown differently, with a legend. A connection's mark follows
  its own evidence.
- **State each fact once.** What the view already shows, such as the environment selected or
  the deployment node a group stands for, is not repeated on each element.
