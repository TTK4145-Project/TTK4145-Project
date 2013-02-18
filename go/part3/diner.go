package main

import (
	"fmt"
	"time"
)

const numOfPhil int =  5

func main() {
	fmt.Println("iCHUZu");

	fork1 := make(chan bool)
	fork2 := make(chan bool)

	go philler(fork1, fork2)

	for i := 1; i < numOfPhil; i++ {
		
	}

	never := make(chan bool)
	<- never;
}

func philler(leftFork chan bool, rightFork chan bool) {
	counter := 0

	for {
		counter++

	}

	fmt.Println("eating: ", counter)

	time.Sleep(1000 * time.Millisecond)
	
	
}

func fork(left, right <- chan bool) {
	for {
		select {
			case <-left:
				<-left
			case <-right:
				<-right
		}
	}
}
