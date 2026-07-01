package com.jpmc.midascore.component;

import com.jpmc.midascore.entity.TransactionRecord;
import com.jpmc.midascore.entity.UserRecord;
import com.jpmc.midascore.foundation.Incentive;
import com.jpmc.midascore.foundation.Transaction;
import com.jpmc.midascore.repository.TransactionRecordRepository;
import com.jpmc.midascore.repository.UserRepository;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.Optional;

@Component
public class TransactionListener {

    private final UserRepository userRepository;
    private final TransactionRecordRepository transactionRecordRepository;
    private final RestTemplate restTemplate;

    public TransactionListener(
            UserRepository userRepository,
            TransactionRecordRepository transactionRecordRepository,
            RestTemplate restTemplate
    ) {
        this.userRepository = userRepository;
        this.transactionRecordRepository = transactionRecordRepository;
        this.restTemplate = restTemplate;
    }

    @KafkaListener(topics = "${general.kafka-topic}", groupId = "midas-core")
    public void listen(Transaction transaction) {
        Optional<UserRecord> senderOptional = userRepository.findById(transaction.getSenderId());
        Optional<UserRecord> recipientOptional = userRepository.findById(transaction.getRecipientId());

        if (senderOptional.isEmpty() || recipientOptional.isEmpty()) {
            return;
        }

        UserRecord sender = senderOptional.get();
        UserRecord recipient = recipientOptional.get();

        if (sender.getBalance() < transaction.getAmount()) {
            return;
        }

        Incentive incentive = restTemplate.postForObject(
                "http://localhost:8080/incentive",
                transaction,
                Incentive.class
        );

        float incentiveAmount = incentive == null ? 0 : incentive.getAmount();

        sender.setBalance(sender.getBalance() - transaction.getAmount());
        recipient.setBalance(recipient.getBalance() + transaction.getAmount() + incentiveAmount);

        userRepository.save(sender);
        userRepository.save(recipient);

        TransactionRecord record = new TransactionRecord(
                sender,
                recipient,
                transaction.getAmount(),
                incentiveAmount
        );

        transactionRecordRepository.save(record);
    }
}
