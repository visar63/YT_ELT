# video_ids = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]


# def batch_list(video_ids, batch_size=4):
#     for i in range(0, len(video_ids), batch_size):
#         yield video_ids[i:i + batch_size] # Yield batches of video IDs, each of size `batch_size`

# def batch_list2(video_ids, batch_size=4):
#     for i in range(0, len(video_ids), batch_size):
#         print(video_ids[i:i + batch_size])
#         return video_ids[i:i + batch_size] # Yield batches of video IDs, each of size `batch_size`

# # for batch in batch_list(video_ids, batch_size=4):
# #     print(batch)

# # for batch2 in batch_list2(video_ids, batch_size=4):
# #     print(batch2)

# for i in batch_list(video_ids, batch_size=4):
#     print(i)


from datetime import date


print(date.today())