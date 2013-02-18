package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println("Printing stuff");

	channel := make(chan int)
	out := make(chan int)

	go server(channel, out)
	go proc1(channel, 5)
	go proc2(channel, 5)
	go proc3(channel, 5)

	// go reader(out)

	for iter := range out {
		fmt.Println(iter)
	}

	// run you fools 
	//never := make(chan int)
	//<- never
}

func server(channel, out chan int) {
	val := 0

	for {
		out <- val
		in :=  <- channel
		val += in
	}
}

func reader(out chan int) {
	val := <- out
	for {
		select {
			case val = <- out:
			default:
		}
		fmt.Println("Value: ", val);
		time.Sleep(1000 * time.Millisecond)
	}
}

func proc1(channel chan int, loopCount int) {
	for i := 0; i < loopCount; i++ {
		val := 1
		channel <- val
	}
	fmt.Println("proc1");
}

func proc2(channel chan int, loopCount int) {
	for i := 0; i < loopCount; i++ {
		val := 10
		channel <- val
	}
	fmt.Println("proc2");
}

func proc3(channel chan int, loopCount int) {
	for i := 0; i < loopCount; i++ {
		val := -1
		channel <- val
	}
	fmt.Println("proc3");
}