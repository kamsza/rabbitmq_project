# RabbbitMQ connection system

The project is an assignment from [Distributed Systems class](https://syllabuskrk.agh.edu.pl/2017-2018/en/magnesite/study_plans/stacjonarne-informatyka/module/iin-1-686-s-zimowy-distributed-systems). The goal of a project is to implement 
an exchange of information between three modules lsted below. 

## Schema

![starting panel](https://github.com/kamsza/rabbitmq_project/blob/master/schema.PNG)


## Task
We have *space agencies*, that sometimes need to make an order. They can order one of three services:
- transport of people,
- transport of cargo,
- placing satellite in the orbit of a planet.

There are also many *carriers*. Each of them can do two of above things. The plan is simple - agency wants the job done, so it places the order in first free carrier, that can realize it. Fees are the same, carriers are equally good, all that matters is time. There is also big brother - *Admin*, that hears everything, and can send some message to all carriers, all agencies or to everybody. 

## Implementation
### Agency

Each agency has unique id, unique queue for incoming messages and access to orders exchange. Agency sends message to echange with appropriate key. After some time it gets return message (with key agency.agency_id), that order is completed.

### Carrier

Each carrire is connected with two of three named queues. QoS set to 1 ensures, that it can realize 1 order in a given time. From queue it gets a message with appropriate properties values (i.a. reply_to set as agency.sender_id). It also has provate queue for messages from admin.

### Admin

Admin hears everything, because it is connected to orders exchange with *#* key. It also has it's own exchange - messages, and can send some message to all connected carriers or agencies. 